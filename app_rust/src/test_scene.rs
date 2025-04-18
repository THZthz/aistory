use vello::kurbo::{Affine, Circle};
use vello::peniko::{Color, Fill};
use vello::Scene;

pub(crate) struct TestScene {}

impl TestScene {
    pub(crate) fn simple_scene(scene: &mut Scene) {
        scene.fill(
            Fill::NonZero,
            Affine::IDENTITY,
            Color::from_rgb8(242, 140, 168),
            None,
            &Circle::new((420.0, 200.0), 120.0),
        );
    }
}