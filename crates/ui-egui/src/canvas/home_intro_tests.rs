//! The Home screen's entrance timing.
use super::*;

#[test]
fn the_entrance_starts_hidden_and_ends_settled_with_no_sweep_left() {
    let start = home_intro_at(0.0);
    assert_eq!((start.glow, start.title, start.rule, start.sweep), (0.0, 0.0, 0.0, None));
    let end = home_intro_at(1.0);
    assert_eq!((end.glow, end.title, end.rule, end.sweep), (1.0, 1.0, 1.0, None));
    let mid = home_intro_at(0.7);
    assert!(mid.sweep.is_some() && mid.title > 0.9 && mid.rule > 0.0, "{mid:?}");
    assert!(home_intro_at(0.3).sweep.is_none() && home_intro_at(0.3).rule == 0.0, "the sweep and the rule wait for the name");
    // Nothing overshoots past fully visible.
    for i in 0..=100 {
        let s = home_intro_at(i as f32 / 100.0);
        assert!(s.glow <= 1.0 && s.title <= 1.0 && s.rule <= 1.0);
    }
}

#[test]
fn with_animations_off_the_home_screen_is_simply_there() {
    let ctx = egui::Context::default();
    ctx.all_styles_mut(|s| s.animation_time = 0.0);
    let mut out = ctx.run_ui(Default::default(), |ui| {
        assert_eq!(home_intro(ui.ctx()), home_intro_at(1.0));
    });
    out.textures_delta.clear();
}

#[test]
fn the_home_card_fits_a_phone_and_stacks_its_buttons() {
    assert_eq!(home_card_width(1200.0), 460.0);
    let phone = home_card_width(315.0);
    assert_eq!(phone, 283.0);
    assert!(phone < 2.0 * HOME_BUTTON + 12.0, "two buttons don't fit side by side, so they stack");
    assert_eq!(home_card_width(50.0), 200.0, "never collapses to nothing");
}
