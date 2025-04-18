use std::sync::Arc;

use skrifa::MetadataProvider;
use skrifa::raw::{FileRef, FontRef};

use vello::kurbo::Affine;
use vello::peniko::{Blob, Brush, BrushRef, Fill, Font, StyleRef, color::palette};
use vello::{Glyph, Scene};

const ROBOTO_FONT: &[u8] = include_bytes!("../assets/fonts/Roboto-Regular.ttf");
const INCONSOLATA_FONT: &[u8] = include_bytes!("../assets/fonts/Inconsolata.ttf");
const NOTO_EMOJI_CBTF_SUBSET: &[u8] = include_bytes!("../assets/fonts/NotoEmoji-CBTF-Subset.ttf");
const NOTO_EMOJI_COLR_SUBSET: &[u8] = include_bytes!("../assets/fonts/NotoEmoji-Subset.ttf");

pub struct SimpleText {
    roboto: Font,
    inconsolata: Font,
    noto_emoji_colr_subset: Font,
    noto_emoji_cbtf_subset: Font,
}

impl SimpleText {
    pub fn new() -> Self {
        Self {
            roboto: Font::new(Blob::new(Arc::new(ROBOTO_FONT)), 0),
            inconsolata: Font::new(Blob::new(Arc::new(INCONSOLATA_FONT)), 0),
            noto_emoji_colr_subset: Font::new(Blob::new(Arc::new(NOTO_EMOJI_COLR_SUBSET)), 0),
            noto_emoji_cbtf_subset: Font::new(Blob::new(Arc::new(NOTO_EMOJI_CBTF_SUBSET)), 0),
        }
    }

    pub fn add_colr_emoji_run<'a>(
        &mut self,
        scene: &mut Scene,
        size: f32,
        transform: Affine,
        glyph_transform: Option<Affine>,
        style: impl Into<StyleRef<'a>>,
        text: &str,
    ) {
        let font = self.noto_emoji_colr_subset.clone();
        self.add_var_run(
            scene,
            Some(&font),
            size,
            &[],
            // This should be unused
            &Brush::Solid(palette::css::WHITE),
            transform,
            glyph_transform,
            style,
            text,
        );
    }

    pub fn add_bitmap_emoji_run<'a>(
        &mut self,
        scene: &mut Scene,
        size: f32,
        transform: Affine,
        glyph_transform: Option<Affine>,
        style: impl Into<StyleRef<'a>>,
        text: &str,
    ) {
        let font = self.noto_emoji_cbtf_subset.clone();
        self.add_var_run(
            scene,
            Some(&font),
            size,
            &[],
            // This should be unused
            &Brush::Solid(palette::css::WHITE),
            transform,
            glyph_transform,
            style,
            text,
        );
    }

    pub fn add_run<'a>(
        &mut self,
        scene: &mut Scene,
        font: Option<&Font>,
        size: f32,
        brush: impl Into<BrushRef<'a>>,
        transform: Affine,
        glyph_transform: Option<Affine>,
        style: impl Into<StyleRef<'a>>,
        text: &str,
    ) {
        self.add_var_run(
            scene,
            font,
            size,
            &[],
            brush,
            transform,
            glyph_transform,
            style,
            text,
        );
    }

    pub fn add_var_run<'a>(
        &mut self,
        scene: &mut Scene,
        font: Option<&Font>,
        size: f32,
        variations: &[(&str, f32)],
        brush: impl Into<BrushRef<'a>>,
        transform: Affine,
        glyph_transform: Option<Affine>,
        style: impl Into<StyleRef<'a>>,
        text: &str,
    ) {
        let default_font = if variations.is_empty() {
            &self.roboto
        } else {
            &self.inconsolata
        };
        let font = font.unwrap_or(default_font);
        let font_ref = to_font_ref(font).unwrap();
        let brush = brush.into();
        let style = style.into();
        let axes = font_ref.axes();
        let font_size = skrifa::instance::Size::new(size);
        let var_loc = axes.location(variations.iter().copied());
        let charmap = font_ref.charmap();
        let metrics = font_ref.metrics(font_size, &var_loc);
        let line_height = metrics.ascent - metrics.descent + metrics.leading;
        let glyph_metrics = font_ref.glyph_metrics(font_size, &var_loc);
        let mut pen_x = 0_f32;
        let mut pen_y = 0_f32;
        scene
            .draw_glyphs(font)
            .font_size(size)
            .transform(transform)
            .glyph_transform(glyph_transform)
            .normalized_coords(bytemuck::cast_slice(var_loc.coords()))
            .brush(brush)
            .hint(false)
            .draw(
                style,
                text.chars().filter_map(|ch| {
                    if ch == '\n' {
                        pen_y += line_height;
                        pen_x = 0.0;
                        return None;
                    }
                    let gid = charmap.map(ch).unwrap_or_default();
                    let advance = glyph_metrics.advance_width(gid).unwrap_or_default();
                    let x = pen_x;
                    pen_x += advance;
                    Some(Glyph {
                        id: gid.to_u32(),
                        x,
                        y: pen_y,
                    })
                }),
            );
    }

    pub fn add(
        &mut self,
        scene: &mut Scene,
        font: Option<&Font>,
        size: f32,
        brush: Option<&Brush>,
        transform: Affine,
        text: &str,
    ) {
        let brush = brush.unwrap_or(&Brush::Solid(palette::css::WHITE));
        self.add_run(
            scene,
            font,
            size,
            brush,
            transform,
            None,
            Fill::NonZero,
            text,
        );
    }
}

impl Default for SimpleText {
    fn default() -> Self {
        Self::new()
    }
}

fn to_font_ref(font: &Font) -> Option<FontRef<'_>> {
    let file_ref = FileRef::new(font.data.as_ref()).ok()?;
    match file_ref {
        FileRef::Font(font) => Some(font),
        FileRef::Collection(collection) => collection.get(font.index).ok(),
    }
}
