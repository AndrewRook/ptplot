import * as p from "core/properties"
import {Circle, CircleView, CircleData} from "models/glyphs/circle"
import {Context2d} from "core/util/canvas"


function _convert_to_bezier(x: number, y: number, radius: number,
                            rot: number): [number, number, number, number,
                                           number, number] {
  //0 degrees is pointing down (in data space), rotation is clockwise
  const [xy0_offset, cx_offset, cy_offset] = _generate_offsets(radius)


  const cosine = -Math.cos(rot * Math.PI / 180)
  const sine = Math.sin(rot * Math.PI / 180)

  const x0 = x - xy0_offset * sine
  const y0 = y + xy0_offset * cosine
  const cx0 = x - cx_offset * cosine + cy_offset * sine
  const cx1 = x + cx_offset * cosine + cy_offset * sine
  const cy0 = y - cx_offset * sine - cy_offset * cosine
  const cy1 = y + cx_offset * sine - cy_offset * cosine
  return [x0, y0, cx0, cx1, cy0, cy1]
}

function _generate_offsets(radius: number): [number, number, number] {
    //Empirically these values basically "work" to make a pick with the same
    //visual radius as a circle
    const adjusted_radius = radius * 3.5
    const xy0_offset = adjusted_radius / 2.5
    const cx_offset = adjusted_radius / 1.
    const cy_offset = adjusted_radius / 2.2
    return [xy0_offset, cx_offset, cy_offset]
}


export type PickData = CircleData & {
  rot: p.UniformVector<number>
}

export interface PickView extends PickData {}

export class PickView extends CircleView {
  model: Pick
  visuals: Pick.Visuals

  protected _render(ctx: Context2d, indices: number[], data?: PickData): void {
    const {sx, sy, sradius} = data ?? this

    const rot = this.rot.array

    for (const i of indices) {
      const sx_i = sx[i]
      const sy_i = sy[i]
      const rot_i = rot[i]
      const sradius_i = sradius[i]

      if (!isFinite(sx_i + sy_i + sradius_i))
        continue

      const [x0, y0, cx0, cx1, cy0, cy1] = _convert_to_bezier(
        sx_i, sy_i, sradius_i, rot_i
      )

      ctx.beginPath()
      ctx.moveTo(x0, y0)
      ctx.bezierCurveTo(cx0, cy0, cx1, cy1, x0, y0)

      if (this.visuals.line.doit) {
        this.visuals.line.set_vectorize(ctx, i)
        ctx.stroke()
      }
      if (this.visuals.fill.doit) {
        this.visuals.fill.set_vectorize(ctx, i)
        ctx.fill()
      }
      if (this.visuals.hatch.doit) {
        this.visuals.hatch.set_vectorize(ctx, i)
        ctx.fill()
      }
    }
  }
}

export namespace Pick {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Circle.Props & {
    rot: p.AngleSpec
  }

  export type Mixins = Circle.Mixins

  export type Visuals = Circle.Visuals

}

export interface Pick extends Pick.Attrs {}

export class Pick extends Circle {
  properties: Pick.Props
  __view_type__: PickView

  constructor(attrs?: Partial<Pick.Attrs>) {
    super(attrs)
  }

  static init_Pick(): void {
    this.prototype.default_view = PickView

    this.define<Pick.Props>(({}) => ({
      rot:  [ p.AngleSpec, {field: "rot"} ]
    }))

  }
}