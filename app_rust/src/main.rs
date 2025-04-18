mod test_scene;
mod text;

use std::num::NonZeroUsize;
use std::sync::Arc;

use winit::application::ApplicationHandler;
use winit::event::WindowEvent;
use winit::event_loop::{ActiveEventLoop, ControlFlow, EventLoop};
use winit::window::{Window, WindowId};

use vello::kurbo::{Affine, Circle, Vec2};
use vello::peniko::color::palette;
use vello::peniko::{Color, Fill};
use vello::wgpu;
use vello::{AaConfig, Renderer, RendererOptions};

use test_scene::TestScene;
use text::SimpleText;

struct App {
    window: Arc<Window>,
    renderer: Option<Renderer>,
    device: Option<wgpu::Device>,
    queue: Option<wgpu::Queue>,
    surface: Option<wgpu::Surface<'static>>,
    simple_text: Option<SimpleText>,
}

impl ApplicationHandler for App {
    fn resumed(&mut self, _event_loop: &ActiveEventLoop) {}

    fn window_event(&mut self, event_loop: &ActiveEventLoop, _id: WindowId, event: WindowEvent) {
        match event {
            WindowEvent::CloseRequested => {
                println!("The close button was pressed; stopping");
                event_loop.exit();
            }
            WindowEvent::RedrawRequested => {
                let window = self.window.as_ref();

                let mut scene = vello::Scene::new();
                TestScene::simple_scene(&mut scene);

                let simple_text = self.simple_text.as_mut().unwrap();
                simple_text.add_colr_emoji_run(
                    &mut scene,
                    51.0,
                    Affine::translate(Vec2::new(100., 250.)),
                    None,
                    Fill::NonZero,
                    "🎉🤠✅",
                );

                // Render to your window/buffer/etc.
                let size = window.inner_size();
                let surface = self.surface.as_ref().unwrap();
                let surface_texture = surface
                    .get_current_texture()
                    .expect("Failed to get surface texture");
                self.renderer.as_mut().unwrap()
                    .render_to_surface(
                        &self.device.as_ref().unwrap(),
                        &self.queue.as_ref().unwrap(),
                        &scene,
                        &surface_texture,
                        &vello::RenderParams {
                            base_color: palette::css::BLACK,
                            width: size.width,
                            height: size.height,
                            antialiasing_method: AaConfig::Msaa16,
                        },
                    )
                    .expect("Failed to render to surface");
                surface_texture.present();

                window.request_redraw();
            }
            _ => (),
        }
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let event_loop = EventLoop::new()?;
    event_loop.set_control_flow(ControlFlow::Poll);

    // Create window.
    let window = Arc::new(event_loop.create_window(Window::default_attributes())?);

    // Initialize wgpu and get handles.
    let instance = wgpu::Instance::new(wgpu::InstanceDescriptor {
        backends: wgpu::Backends::VULKAN,
        flags: Default::default(),
        dx12_shader_compiler: Default::default(),
        gles_minor_version: Default::default(),
    });

    let surface = unsafe {
        let window_ptr = Arc::as_ptr(&window);
        instance.create_surface(&*window_ptr)?
    };

    let adapter = instance
        .request_adapter(&wgpu::RequestAdapterOptions {
            power_preference: wgpu::PowerPreference::default(),
            compatible_surface: Some(&surface),
            force_fallback_adapter: false,
        })
        .await
        .expect("Failed to find an appropriate adapter");
    let (device, queue) = adapter
        .request_device(
            &wgpu::DeviceDescriptor {
                label: None,
                required_features: Default::default(),
                required_limits: Default::default(),
                memory_hints: Default::default(),
            },
            None,
        )
        .await
        .expect("Failed to create device");

    let surface_caps = surface.get_capabilities(&adapter);
    let format = surface_caps
        .formats
        .iter()
        .find(|&&f| f == wgpu::TextureFormat::Rgba8Unorm || f == wgpu::TextureFormat::Bgra8Unorm)
        .copied()
        .unwrap_or_else(|| {
            println!(
                "Warning: Using fallback format {:?}",
                surface_caps.formats[0]
            );
            surface_caps.formats[0]
        });
    let size = window.inner_size();
    let config = wgpu::SurfaceConfiguration {
        usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
        format,
        width: size.width,
        height: size.height,
        present_mode: wgpu::PresentMode::Fifo,
        desired_maximum_frame_latency: 0,
        alpha_mode: surface_caps.alpha_modes[0],
        view_formats: vec![],
    };
    surface.configure(&device, &config);

    let renderer = Renderer::new(
        &device,
        RendererOptions {
            surface_format: Some(format),
            use_cpu: false,
            antialiasing_support: vello::AaSupport::all(),
            num_init_threads: NonZeroUsize::new(1),
        },
    )
    .expect("Failed to create renderer");

    // Start app.
    let mut app = App {
        window,
        renderer: Some(renderer),
        device: Some(device),
        queue: Some(queue),
        surface: Some(surface),
        simple_text: Some(SimpleText::default()),
    };
    event_loop.run_app(&mut app)?;
    Ok(())
}
