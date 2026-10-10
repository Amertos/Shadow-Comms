# Importing ShadowComms CAD into Onshape

CadQuery exports STEP files. Onshape consumes STEP directly and keeps the feature tree editable, so importing is the cleanest path.

## Steps

1. Go to <https://www.onshape.com/> and sign in (free account is fine for public documents).
2. On the **Documents** page click **Create → Import files**.
3. Drag in, in this order:
   - `cad/exports/shell_bottom.step`
   - `cad/exports/shell_top.step`
   - `cad/exports/shadowcomms_assembly.step` *(pre-arranged preview, optional)*
4. Each STEP becomes a Part Studio tab automatically. Open the tab to pan/rotate the model.
5. If you want a single assembly with both parts placed, create a new **Assembly** tab and insert both Part Studios; the parts are already positioned by the source script.

## Modify freely

Because Onshape re-opens the STEP as a parametric Part Studio, you can:

- Sketch on any face to add notches, engrave the logo, or reposition cutouts.
- Use **Measure** to check clearances (e.g. e-paper window is sized 67.4 × 30.6 mm including 0.3 mm printer clearance).
- If you change a cutout, regenerate the local export with:
  ```bash
  E:/shadowcomms_venv/Scripts/python cad/build_enclosure.py
  ```
  and re-import to keep the repo copy of STEP/STL in sync.

## Printing notes (for Week 6 build)

- Print with 0.2 mm layers, 3 perimeters, ~15 % infill, no supports (lip faces up).
- STEP is the *source*, STL is the *printable* version — commit both.
