import bpy
import sys
import os
from math import radians

def cleanup_scene():
    if bpy.context.object:
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    for block in [bpy.data.meshes, bpy.data.materials, bpy.data.curves]:
        for item in block:
            if item.users == 0:
                block.remove(item)

def import_svg(svg_path):
    if not os.path.exists(svg_path):
        raise FileNotFoundError(f"SVG file not found at {svg_path}")

    before = set(bpy.data.objects)
    try:
        bpy.ops.import_curve.svg(filepath=svg_path)
    except Exception as e:
        raise RuntimeError(f"SVG import failed: {str(e)}")

    after = set(bpy.data.objects)
    new_objects = after - before

    if not new_objects:
        raise RuntimeError("SVG import created no objects")

    logo_obj = new_objects.pop()
    bpy.ops.object.select_all(action='DESELECT')
    logo_obj.select_set(True)
    bpy.context.view_layer.objects.active = logo_obj

    return logo_obj

def process_logo(logo_obj, params):
    if not logo_obj:
        raise ValueError("No logo object provided")

    bpy.ops.object.select_all(action='DESELECT')
    logo_obj.select_set(True)
    bpy.context.view_layer.objects.active = logo_obj

    if logo_obj.type == 'CURVE':
        logo_obj.data.dimensions = '3D'
        if params['depth'] > 0:
            logo_obj.data.extrude = params['depth']

        # ✅ Only convert to mesh — don't apply fill again
        logo_obj.data.dimensions = '2D'
        logo_obj.data.fill_mode = 'BOTH'  # or 'FRONT'
        bpy.ops.object.convert(target='MESH')

    # ✅ No fill here — original shape is preserved

    scale_val = params['scale']
    if scale_val != 1.0:
        logo_obj.scale = (scale_val, scale_val, scale_val)
        bpy.ops.object.transform_apply(scale=True)

    orientation_map = {
        'x': (radians(90), 0, 0),
        'y': (0, radians(90), 0),
        'z': (0, 0, radians(90)),
        '-x': (radians(-90), 0, 0),
        '-y': (0, radians(-90), 0),
        '-z': (0, 0, radians(-90))
    }

    orientation = params['orientation'].lower()
    if orientation in orientation_map:
        logo_obj.rotation_euler = orientation_map[orientation]

    # Gloss material
    material = bpy.data.materials.new(name="GlossyMaterial")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs['Roughness'].default_value = 1.0 - params['gloss']
    logo_obj.data.materials.append(material)


def main():
    try:
        print("🔧 Starting SVG to GLB conversion...")
        args = sys.argv[sys.argv.index("--") + 1:]

        params = {
            'svg_path': args[0],
            'depth': float(args[1]),
            'gloss': float(args[2]),
            'scale': float(args[3]),
            'orientation': args[4],
            'overlay': args[5] if args[5].lower() != 'null' else None,
            'output_paths': {
                'glb': args[6],
                'usdz': args[7]
            }
        }

        if params['depth'] < 0:
            raise ValueError("Depth cannot be negative")
        if not 0 <= params['gloss'] <= 1:
            raise ValueError("Gloss must be between 0 and 1")

        cleanup_scene()
        logo_obj = import_svg(params['svg_path'])
        process_logo(logo_obj, params)

        bpy.ops.export_scene.gltf(
            filepath=params['output_paths']['glb'],
            export_format='GLB',
            export_yup=True,
            export_apply=True,
            use_selection=True
        )

        try:
            bpy.ops.wm.usd_export(
                filepath=params['output_paths']['usdz'],
                selected_objects_only=True
            )
        except Exception as e:
            print(f"Warning: USDZ export failed - {str(e)}")

        print("✅ Model generation completed successfully")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
