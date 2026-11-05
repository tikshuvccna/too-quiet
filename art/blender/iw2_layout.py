"""World-2 interiors: layout data shared by the Blender scripts and the pack step (no bpy import here).

PLACE[house][object_id] = (x, y, z, footprint) in room world units (x -7..7, y -4.5..4.5 back wall, z = height of the
sprite anchor above the floor for wall objects). footprint = (rx, ry) soft contact shadow, None = wall object.
Interactive ids (not x_*) must equal the ids in content/he/world/houses_world.json.
"""
WIN_X = {"inn": 3.6, "bell_tower": 3.4, "tailor": -3.0, "school": 4.4, "fisher": -3.2, "workshop": 4.4, "library": 4.4,
         "observatory": 3.6, "stories": -3.8, "farm": 4.2, "shepherd": 3.2, "herbs": 4.4, "fairy": 4.4, "guild": 4.4,
         "lighthouse": 3.0}

ORDER = ["inn", "bell_tower", "tailor", "school", "fisher", "workshop", "library", "observatory", "stories", "farm",
         "shepherd", "herbs", "fairy", "guild", "lighthouse"]

PLACE = {
    "inn": {
        "i_board": (-5.3, 4.45, 1.5, None), "i_key": (-3.0, 4.45, 1.8, None), "i_rules": (1.3, 4.45, 2.2, None),
        "i_guestbook": (3.6, 1.6, 0, (0.45, 0.35)), "i_kettle": (6.0, 3.6, 0, (0.6, 0.4)), "i_lost": (6.0, -1.3, 0, (0.8, 0.5)),
        "x_hearth": (-0.8, 4.05, 0, (1.3, 0.5)), "x_long_table": (-1.8, -0.5, 0, (2.4, 0.8)), "x_barrels": (-5.9, 2.2, 0, (0.8, 0.5)),
        "x_coat_rack": (-6.2, -2.3, 0, (0.3, 0.25)), "x_plant": (6.3, 1.1, 0, (0.4, 0.3)),
    },
    "bell_tower": {
        "b_window": (0.3, 4.45, 1.3, None), "b_rope": (-1.4, 3.9, 0, (0.35, 0.3)), "b_notes": (-3.0, 2.0, 0, (0.5, 0.4)),
        "b_pigeon": (3.4, 3.4, 0, (0.45, 0.35)), "b_oil": (5.6, 1.6, 0, (0.55, 0.4)),
        "x_stairs": (-5.2, 2.8, 0, (1.0, 0.8)), "x_bell_wheel": (-5.2, -1.0, 0, (0.9, 0.6)), "x_rope_coil": (-2.4, -2.4, 0, (0.55, 0.4)),
        "x_crate_pile": (6.0, -1.7, 0, (0.7, 0.5)), "x_lantern": (2.6, -2.7, 0, (0.3, 0.25)),
    },
    "tailor": {
        "t_shop": (0.3, 4.45, 2.3, None), "t_list": (-0.95, 4.45, 1.9, None), "t_threads": (-5.7, 2.4, 0, (0.55, 0.4)),
        "t_mannequin": (-0.9, 1.9, 0, (0.4, 0.3)), "t_basket": (5.9, 3.5, 0, (0.5, 0.4)),
        "x_cloth_shelf": (3.0, 4.1, 0, (1.4, 0.4)), "x_cutting_table": (1.8, -0.9, 0, (1.2, 0.55)),
        "x_sewing": (-3.8, 0.2, 0, (0.8, 0.5)), "x_mirror": (-5.6, -1.7, 0, (0.6, 0.3)), "x_hat_stand": (6.3, 1.2, 0, (0.3, 0.25)),
    },
    "school": {
        "s_board": (-2.4, 4.45, 1.2, None), "s_drawings": (1.5, 4.45, 1.9, None), "s_notes": (-2.4, 2.8, 0, (1.0, 0.5)),
        "s_globe": (5.4, 2.5, 0, (0.5, 0.4)), "s_bench": (3.0, -2.5, 0, (1.2, 0.5)),
        "x_desks_a": (-3.6, 0.4, 0, (1.4, 0.6)), "x_desks_b": (-0.2, -0.9, 0, (1.4, 0.6)), "x_bookcase": (-5.9, 3.5, 0, (0.8, 0.4)),
        "x_stove": (6.2, 0.5, 0, (0.5, 0.4)), "x_easel": (-6.0, -2.0, 0, (0.5, 0.3)),
    },
    "fisher": {
        "f_net": (2.0, 4.45, 0.9, None), "f_map": (-0.1, 4.45, 1.9, None), "f_lamp": (6.0, 3.4, 0, (0.3, 0.25)),
        "f_log": (-5.3, 2.0, 0, (0.55, 0.45)), "f_boat": (2.6, -1.6, 0, (1.8, 0.8)),
        "x_barrels": (-6.0, -0.9, 0, (0.8, 0.5)), "x_fish_rack": (-0.6, 1.4, 0, (1.2, 0.4)), "x_rods": (6.4, 1.0, 0, (0.3, 0.25)),
        "x_buoys": (-3.6, -2.7, 0, (0.7, 0.4)), "x_bucket": (-1.0, -2.9, 0, (0.4, 0.3)),
    },
    "workshop": {
        "w_gears": (-3.2, 4.45, 0.9, None), "w_note": (-0.4, 4.45, 2.1, None), "w_clocks": (1.7, 4.45, 2.3, None),
        "w_bench": (-2.6, 1.4, 0, (1.6, 0.7)), "w_tester": (3.0, 1.8, 0, (0.6, 0.5)),
        "x_tool_rack": (-6.0, 3.5, 0, (0.9, 0.4)), "x_grinder": (5.9, 1.4, 0, (0.5, 0.4)), "x_gear_bin": (5.6, -1.9, 0, (0.7, 0.5)),
        "x_anvil": (0.6, -1.9, 0, (0.6, 0.4)), "x_parts_shelf": (-5.8, -1.7, 0, (0.8, 0.4)),
    },
    "library": {
        "l_catalog": (1.5, 4.1, 0, (0.8, 0.4)), "l_ladder": (-2.9, 3.4, 0, (0.8, 0.4)), "l_table": (1.2, 0.3, 0, (1.4, 0.8)),
        "l_cover": (-4.2, 1.0, 0, (0.5, 0.4)), "l_stamp": (5.4, 1.4, 0, (0.7, 0.45)),
        "x_shelves_a": (-4.7, 4.1, 0, (1.4, 0.4)), "x_shelves_b": (-1.4, 4.1, 0, (1.4, 0.4)), "x_spool_rack": (6.3, 3.6, 0, (0.8, 0.4)),
        "x_reading_chair": (-2.0, -1.5, 0, (0.7, 0.5)), "x_lamp": (3.8, -2.3, 0, (0.3, 0.2)),
    },
    "observatory": {
        "o_chart": (-3.4, 4.45, 1.6, None), "o_telescope": (0.2, 1.2, 0, (0.8, 0.6)), "o_orrery": (-4.4, 0.4, 0, (0.7, 0.5)),
        "o_log": (-5.5, 2.3, 0, (0.7, 0.45)), "o_tea": (4.9, 2.0, 0, (0.5, 0.4)),
        "x_chart_table": (2.4, -1.9, 0, (1.2, 0.7)), "x_armillary": (-2.6, -1.8, 0, (0.5, 0.4)), "x_stool": (5.8, -0.8, 0, (0.35, 0.3)),
        "x_book_cart": (-1.0, 3.7, 0, (0.8, 0.4)), "x_blanket_chair": (6.2, 3.7, 0, (0.7, 0.5)),
    },
    "stories": {
        "st_fire": (0.0, 0.7, 0, (1.4, 1.0)), "st_curtain": (3.6, 4.45, 0.0, None), "st_book": (-2.0, 3.2, 0, (0.5, 0.4)),
        "st_puppets": (5.8, 1.4, 0, (0.7, 0.5)), "st_drum": (-5.5, -0.5, 0, (0.7, 0.5)),
        "x_bench_front": (0.0, -2.7, 0, (1.7, 0.4)), "x_bench_left": (-3.4, 0.9, 0, (0.4, 1.2)), "x_bench_right": (3.4, 0.9, 0, (0.4, 1.2)),
        "x_log_stack": (-6.1, 3.2, 0, (0.8, 0.5)), "x_lantern": (6.3, -2.3, 0, (0.3, 0.25)),
    },
    "farm": {
        "fa_horn": (-1.2, 4.45, 2.4, None), "fa_barn": (-4.6, 4.45, 0.0, None), "fa_cart": (5.6, 1.2, 0, (1.4, 0.7)),
        "fa_ledger": (-2.0, 2.6, 0, (0.6, 0.4)), "fa_cow": (-1.0, -1.8, 0, (1.1, 0.6)),
        "x_stove": (1.0, 4.1, 0, (0.9, 0.4)), "x_kitchen_table": (2.8, -0.9, 0, (1.0, 0.7)), "x_milk_cans": (6.2, -2.4, 0, (0.6, 0.4)),
        "x_sacks": (-6.0, 0.6, 0, (0.7, 0.5)), "x_tool_rack": (6.3, 3.8, 0, (0.7, 0.3)),
    },
    "shepherd": {
        "sh_window": (-4.6, 4.45, 1.5, None), "sh_names": (-2.2, 4.45, 1.5, None), "sh_flute": (0.3, 4.45, 2.1, None),
        "sh_bed": (-4.4, 0.8, 0, (1.3, 0.8)), "sh_blanket": (4.8, 0.4, 0, (0.9, 0.6)),
        "x_stove": (6.0, 3.6, 0, (0.6, 0.4)), "x_wool_bales": (-1.2, 3.6, 0, (0.9, 0.5)), "x_staff_rack": (-6.2, -2.0, 0, (0.4, 0.3)),
        "x_table": (0.8, 0.0, 0, (0.8, 0.6)), "x_hay": (3.4, -2.3, 0, (0.8, 0.5)),
    },
    "herbs": {
        "h_room1": (-5.0, 4.45, 0.0, None), "h_room2": (-2.4, 4.45, 0.0, None), "h_room3": (0.2, 4.45, 0.0, None),
        "h_pot": (1.8, 1.4, 0, (0.5, 0.4)), "h_labels": (3.4, -0.7, 0, (0.5, 0.4)),
        "x_herb_rack": (-3.6, 1.6, 0, (1.3, 0.5)), "x_potting_bench": (5.8, -1.5, 0, (1.0, 0.5)), "x_watering_can": (-6.0, -0.9, 0, (0.4, 0.3)),
        "x_rain_barrel": (6.4, 3.3, 0, (0.5, 0.4)), "x_planter_bed": (-1.0, -2.5, 0, (1.6, 0.6)),
    },
    "fairy": {
        "fy_doors": (-3.0, 4.45, 1.2, None), "fy_blank": (0.2, 4.45, 0.8, None), "fy_post": (-5.6, 2.0, 0, (0.4, 0.3)),
        "fy_lamps": (2.8, 2.6, 0, (0.4, 0.3)), "fy_stairs": (6.0, 2.2, 0, (0.9, 0.7)),
        "x_mushrooms_a": (-2.4, -1.6, 0, (0.7, 0.5)), "x_mushrooms_b": (3.6, -1.8, 0, (0.7, 0.5)), "x_acorn_table": (0.4, 0.6, 0, (0.6, 0.45)),
        "x_leaf_chair": (-1.6, 1.4, 0, (0.45, 0.35)), "x_fern": (-6.0, -0.4, 0, (0.5, 0.4)),
    },
    "guild": {
        "g_banner": (-3.4, 4.45, 1.4, None), "x_banner_b": (-0.2, 4.45, 1.4, None), "g_minutes": (-5.4, 2.4, 0, (0.55, 0.4)),
        "g_model": (1.8, 2.3, 0, (0.6, 0.5)), "g_loom": (-5.0, 0.4, 0, (1.0, 0.7)), "g_chair": (3.6, -1.6, 0, (0.45, 0.4)),
        "x_loom_b": (6.0, 0.6, 0, (0.9, 0.6)), "x_table": (0.2, -1.6, 0, (2.8, 0.9)), "x_candelabra": (-1.8, 3.4, 0, (0.35, 0.3)),
        "x_chest": (6.2, -2.8, 0, (0.7, 0.4)),
    },
    "lighthouse": {
        "lh_lamp": (-0.4, 1.4, 0, (0.9, 0.7)), "lh_telegraph": (-3.4, 4.45, 1.4, None), "lh_mirror": (-5.4, 1.6, 0, (0.6, 0.3)),
        "lh_log": (-2.4, 2.6, 0, (0.5, 0.4)), "lh_tea": (4.8, 2.2, 0, (0.5, 0.4)),
        "x_spiral_stair": (-0.4, 3.9, 0, (1.0, 0.7)), "x_rope_coil": (5.6, 0.2, 0, (0.55, 0.4)), "x_oil_barrels": (6.2, -2.1, 0, (0.8, 0.5)),
        "x_sea_chest": (-3.6, -1.9, 0, (0.8, 0.45)), "x_brass_lantern": (2.4, -2.2, 0, (0.3, 0.25)),
    },
}
