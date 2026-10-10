"""
ShadowComms Enclosure — parametric 2-part case (Week 2 CAD build)

Build decision notes (kept as comments for the journal):
- Body: two shell halves 120 x 70 x 25 mm total, 2 mm wall, snap-fit lip + M2.5 screws.
- Top half holds: 2.9" E-Paper window 66.7 x 29.4 mm (43 ppi margin), SMA antenna bushing,
  USB-C slot, 3 keyboard-area slots for the mini QWERTY module.
- Bottom half holds: PCB shelf at 4mm, battery tray, 4x M2.5 boss at 104 x 54 cc,
  speaker/root for the piezo.

Parts:
  - shell_bottom.step  (lower innen pod + bosses)
  - shell_top.step     (upper cutouts)
  - both as STL for printing test.

Run with:  E:/shadowcomms_venv/Scripts/python build_enclosure.py
"""

import os
import sys
import math
import cadquery as cq
from cadquery import exporters

# ---------------------------------------------------------------- parameters
L, W, H = 120.0, 70.0, 25.0          # outside envelope
WALL = 2.0                            # wall thickness
LIP = 1.2                             # snap lip height
CLEAR = 0.3                           # printer clearance
FILLET_R = 4.0

# E-paper 2.9" (Waveshare uses 29.4x66.7 mm active area; module PCB is a bit larger)
EPD_W, EPD_H = 67.0, 30.0

# SMA antenna bushing hole on left edge of the top half
SMA_ORIFICE = 6.4                      # through-hole dia.
SMA_POS = (8.0, 46.0)                  # x from left, y from bottom (mm)

# USB-C slot on the bottom edge
USBC_W, USBC_H = 10.0, 4.0
USBC_Y = 3.0                           # centered on bottom edge

# Keyboard slots (mini QWERTY membrane ~ 60 x 20 mm active area)
KB_SLOTS = 3
KB_W, KB_H = 18.0, 20.0
KB_GAP = 2.0

# Screw bosses / PCB shelf
BOSS_D, BOSS_ID = 6.0, 2.5
BOSS_OFFSET = 4.0
PCB_HOLD_H = 4.0                       # bottom-shell inner floor to PCB top
BATT_BOX = (34.0, 50.0, 8.5)           # LiPo 803048 approx

OUT = os.path.join(os.path.dirname(__file__), "exports")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- bottom shell
def shell_bottom():
    sk = (
        cq.Workplane("XY")
        .rect(L, W)
        .extrude(H / 2)
        .edges("|Z")
        .fillet(FILLET_R)
        .faces("<Z")
        .workplane()
        .rect(L - 2 * WALL, W - 2 * WALL)
        .cutBlind(-H / 2 + WALL)  # hollow
    )

    # lip ridge on the parting plane
    lip = (
        cq.Workplane("XY")
        .workplane(offset=H / 2 - 0.01)
        .rect(L - 2 * WALL, W - 2 * WALL)
        .extrude(LIP / 2)
        .edges("|Z")
        .fillet(FILLET_R - WALL)
    )
    sk = sk.union(lip)

    # 4 screw bosses at bottom
    for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        bx, by = L / 2 - BOSS_OFFSET, W / 2 - BOSS_OFFSET
        boss = (
            cq.Workplane("XY")
            .center(sx * bx, sy * by)
            .circle(BOSS_D / 2)
            .extrude(H / 2 - WALL)
            .faces(">Z")
            .workplane()
            .hole(BOSS_ID)
        )
        sk = sk.union(boss)

    # PCB shelf pins (simple press fit columns)
    for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        px, py = L / 2 - 14.0, W / 2 - 8.0
        pin = (
            cq.Workplane("XY")
            .center(sx * px, sy * py)
            .circle(1.6)
            .extrude(PCB_HOLD_H + 1.0)
        )
        sk = sk.union(pin)

    # battery pocket (shallow recess on the outer floor)
    batt = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .center(-14.0, 0)
        .rect(BATT_BOX[0], BATT_BOX[1])
        .extrude(BATT_BOX[2])
    )
    sk = sk.cut(batt)

    # USB-C slot on the front face (y = -W/2)
    usbc = (
        cq.Workplane("XY")
        .center(34.0, -W / 2 - 0.5)
        .rect(USBC_W, USBC_H * 2)
        .extrude(WALL * 4, both=True)
    )
    sk = sk.cut(usbc)
    return sk

# ---------------------------------------------------------------- top shell
def shell_top():
    sk = (
        cq.Workplane("XY")
        .workplane(offset=H / 2)
        .rect(L, W)
        .extrude(H / 2)
        .edges("|Z")
        .fillet(FILLET_R)
        .faces("<Z")
        .workplane()
        .rect(L - 2 * WALL, W - 2 * WALL)
        .cutBlind(-H / 2 + WALL)  # hollow
    )

    # lip groove (slightly oversized so the two shells mate)
    groove = (
        cq.Workplane("XY")
        .workplane(offset=H / 2 - 0.01)
        .rect(L - 2 * WALL - CLEAR * 2, W - 2 * WALL - CLEAR * 2)
        .extrude(LIP / 2 + CLEAR)
        .edges("|Z")
        .fillet(FILLET_R - WALL - CLEAR)
    )
    # only the groove (a recess), not the whole cylinder: cut only the lip volume
    sk = sk.cut(groove.faces(">Z").workplane().rect(L - 2 * WALL - CLEAR * 2, W - 2 * WALL - CLEAR * 2).extrude(LIP / 2))

    # e-paper viewing window
    epd_cut = (
        cq.Workplane("XY")
        .workplane(offset=H)
        .center(18.0, 0)
        .rect(EPD_W + 2 * CLEAR, EPD_H + 2 * CLEAR)
        .extrude(2.0)
    )
    sk = sk.cut(epd_cut)

    # SMA antenna orifice on the left face
    sma = (
        cq.Workplane("YZ")
        .workplane(offset=-L / 2 - 0.5)
        .center(SMA_POS[1], H / 2 + SMA_POS[0] * 0.0)
        .circle(SMA_ORIFICE / 2)
        .extrude(WALL * 4, both=True)
    )
    sk = sk.cut(sma)

    # keyboard slots on the right portion of the top face
    for i in range(KB_SLOTS):
        kx = -14.0 - (KB_W / 2 + KB_GAP) * KB_SLOTS / 2 + i * (KB_W + KB_GAP)
        kb = (
            cq.Workplane("XY")
            .workplane(offset=H)
            .center(kx, 0)
            .rect(KB_W, KB_H)
            .extrude(2.0)
        )
        sk = sk.cut(kb)

    # 4 matching countersinks for M2.5 screws
    for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        bx, by = L / 2 - BOSS_OFFSET, W / 2 - BOSS_OFFSET
        cs = (
            cq.Workplane("XY")
            .workplane(offset=H)
            .center(sx * bx, sy * by)
            .circle(BOSS_ID / 2)
            .extrude(2.0)
            .faces(">Z")
            .workplane()
            .circle(4.7)
            .cutBlind(-1.6)
        )
        sk = sk.cut(cs)
    return sk

# ---------------------------------------------------------------- helpers
def export(part, name):
    step = os.path.join(OUT, name + ".step")
    stl = os.path.join(OUT, name + ".stl")
    cq.exporters.export(part, step, exporters.ExportTypes.STEP)
    cq.exporters.export(part, stl, exporters.ExportTypes.STL, tolerance=0.05, angularTolerance=0.2)
    print("exported", step, "and", stl)

def drawing(part, name):
    svg = os.path.join(OUT, name + "_iso.svg")
    exporters.export(
        part,
        svg,
        exporters.ExportTypes.SVG,
        opt={
            "width": 400,
            "height": 300,
            "marginLeft": 10,
            "marginTop": 10,
            "projectionDir": (1, 1, 1),
        },
    )
    print("exported", svg)

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    bot = shell_bottom()
    top = shell_top()
    export(bot, "shell_bottom")
    export(top, "shell_top")
    drawing(bot, "shell_bottom")
    drawing(top, "shell_top")

    # assembly preview (both shells, 6 mm apart)
    asm = bot.union(top.translate((0, 0, H + 6)))
    export(asm, "shadowcomms_assembly")
    drawing(asm, "shadowcomms_assembly")
    print("done.")
