import {FillVector} from "core/property_mixins"
import * as visuals from "core/visuals"
import {BezierView, BezierData, Bezier} from "models/glyphs/bezier"
import * as p from "core/properties"
import {Context2d} from "core/util/canvas"

export type BezierFillData = BezierData & {}

export interface BezierFillView extends BezierFillData {}

export class BezierFillView extends BezierView {
  model: BezierFill
  visuals: BezierFill.Visuals

  _render(ctx: Context2d, indices: number[], data? : BezierFillData): void {
    const {sx0, sy0, sx1, sy1, scx0, scy0, scx1, scy1} = data ?? this

    for (const i of indices) {
      const sx0_i = sx0[i]
      const sy0_i = sy0[i]
      const sx1_i = sx1[i]
      const sy1_i = sy1[i]
      const scx0_i = scx0[i]
      const scy0_i = scy0[i]
      const scx1_i = scx1[i]
      const scy1_i = scy1[i]

      if (!isFinite(sx0_i + sy0_i + sx1_i + sy1_i + scx0_i + scy0_i + scx1_i + scy1_i))
        continue

      ctx.beginPath()
      ctx.moveTo(sx0_i, sy0_i)
      ctx.bezierCurveTo(scx0_i, scy0_i, scx1_i, scy1_i, sx1_i, sy1_i)

      if (this.visuals.line.doit) {
        this.visuals.line.set_vectorize(ctx, i)
        ctx.stroke()
      }
      if (this.visuals.fill.doit) {
        this.visuals.fill.set_vectorize(ctx, i)
        ctx.fill()
      }
    }
  }
}

export namespace BezierFill {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Bezier.Props & {
  } & Mixins

  export type Mixins = FillVector

  export type Visuals = Bezier.Visuals & {fill: visuals.FillVector}
  //console.log(Bezier.Visuals)
}

export interface BezierFill extends BezierFill.Attrs {}

export class BezierFill extends Bezier {
  properties: BezierFill.Props
  __view_type__: BezierFillView

  constructor(attrs?: Partial<BezierFill.Attrs>) {
    super(attrs)
  }

  static init_BezierFill(): void {
    this.prototype.default_view = BezierFillView
    this.mixins<BezierFill.Mixins>([FillVector])
  }

}
