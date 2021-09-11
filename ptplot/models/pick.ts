//All of this adapted from the bokeh bezier glyph
import {FillVector, LineVector} from "@bokehjs/core/property_mixins"
import * as visuals from "@bokehjs/core/visuals"
import {Rect, FloatArray, ScreenArray} from "@bokehjs/core/types"
import {SpatialIndex} from "@bokehjs/core/util/spatial"
import {Context2d} from "@bokehjs/core/util/canvas"
import {Glyph, GlyphView, GlyphData} from "@bokehjs/models/glyphs/glyph"
import {inplace} from "@bokehjs/core/util/projections"
import * as p from "@bokehjs/core/properties"

// algorithm adapted from http://stackoverflow.com/a/14429749/3406693
function _cbb(x0: number, y0: number,
              x1: number, y1: number,
              x2: number, y2: number,
              x3: number, y3: number): [number, number, number, number] {
  const tvalues: number[] = []
  const bounds: [number[], number[]] = [[], []]

  for (let i = 0; i <= 2; i++) {
    let a, b, c
    if (i === 0) {
      b = ((6 * x0) - (12 * x1)) + (6 * x2)
      a = (((-3 * x0) + (9 * x1)) - (9 * x2)) + (3 * x3)
      c = (3 * x1) - (3 * x0)
    } else {
      b = ((6 * y0) - (12 * y1)) + (6 * y2)
      a = (((-3 * y0) + (9 * y1)) - (9 * y2)) + (3 * y3)
      c = (3 * y1) - (3 * y0)
    }

    if (Math.abs(a) < 1e-12) { // Numerical robustness
      if (Math.abs(b) < 1e-12) // Numerical robustness
        continue
      const t = -c / b
      if (0 < t && t < 1)
        tvalues.push(t)
      continue
    }

    const b2ac = (b * b) - (4 * c * a)
    const sqrtb2ac = Math.sqrt(b2ac)

    if (b2ac < 0)
      continue

    const t1 = (-b + sqrtb2ac) / (2 * a)
    if (0 < t1 && t1 < 1)
      tvalues.push(t1)

    const t2 = (-b - sqrtb2ac) / (2 * a)
    if (0 < t2 && t2 < 1)
      tvalues.push(t2)
  }

  let j = tvalues.length
  const jlen = j
  while (j--) {
    const t = tvalues[j]
    const mt = 1 - t
    const x = (mt * mt * mt * x0) + (3 * mt * mt * t * x1) + (3 * mt * t * t * x2) + (t * t * t * x3)
    bounds[0][j] = x
    const y = (mt * mt * mt * y0) + (3 * mt * mt * t * y1) + (3 * mt * t * t * y2) + (t * t * t * y3)
    bounds[1][j] = y
  }

  bounds[0][jlen] = x0
  bounds[1][jlen] = y0
  bounds[0][jlen + 1] = x3
  bounds[1][jlen + 1] = y3

  return [
    Math.min(...bounds[0]),
    Math.max(...bounds[1]),
    Math.max(...bounds[0]),
    Math.min(...bounds[1]),
  ]
}

function _convert_to_bezier(x: number, y: number,
                            rot: number, xy0_offset: number,
                            cx_offset: number, cy_offset: number): [number, number, number, number,
                                                            number, number] {
  const cosine = -Math.cos(rot * Math.PI / 180)
  const sine = Math.sin(rot * Math.PI / 180)

  const x0 = x - xy0_offset * sine
  const y0 = y - xy0_offset * cosine
  const cx0 = x - cx_offset * cosine + cy_offset * sine
  const cx1 = x + cx_offset * cosine + cy_offset * sine
  const cy0 = y + cx_offset * sine + cy_offset * cosine
  const cy1 = y - cx_offset * sine + cy_offset * cosine
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

export type PickData = GlyphData & p.UniformsOf<Pick.Mixins> & {
  radius: p.UniformScalar<number>
  _x: FloatArray
  _y: FloatArray
  rot: p.UniformVector<number>
  _x0: FloatArray
  _y0: FloatArray
  _x1: FloatArray
  _y1: FloatArray
  _cx0: FloatArray
  _cy0: FloatArray
  _cx1: FloatArray
  _cy1: FloatArray

  sx0: ScreenArray
  sy0: ScreenArray
  sx1: ScreenArray
  sy1: ScreenArray
  scx0: ScreenArray
  scy0: ScreenArray
  scx1: ScreenArray
  scy1: ScreenArray
}

export interface PickView extends PickData {}

export class PickView extends GlyphView {
  model: Pick
  visuals: Pick.Visuals

  protected _project_data(): void {
    inplace.project_xy(this._x, this._y)
    inplace.project_xy(this._x0, this._y0)
    inplace.project_xy(this._x1, this._y1)
  }

  protected _set_data(): void {
    const rot = this.rot.array

    const [xy0_offset, cx_offset, cy_offset] = _generate_offsets(this.radius.value)
    const length = this._x.length
    this._x0 = new Float64Array(length)
    this._y0 = new Float64Array(length)
    this._cx0 = new Float64Array(length)
    this._cy0 = new Float64Array(length)
    this._cx1 = new Float64Array(length)
    this._cy1 = new Float64Array(length)
    for (let i = 0; i < length; i++) {
        [this._x0[i], this._y0[i], this._cx0[i], this._cx1[i], this._cy0[i], this._cy1[i]] = _convert_to_bezier(
            this._x[i], this._y[i], rot[i], xy0_offset, cx_offset, cy_offset
        )
    }
    this._x1 = this._x0
    this._y1 = this._y0
  }

  protected _map_data(): void {
    const {x_scale, y_scale} = this.renderer.coordinates

    this.sx0 = this.sx1 = x_scale.v_compute(this._x0)
    this.sy0 = this.sy1 = y_scale.v_compute(this._y0)
    this.scx0 = x_scale.v_compute(this._cx0)
    this.scx1 = x_scale.v_compute(this._cx1)
    this.scy0 = y_scale.v_compute(this._cy0)
    this.scy1 = y_scale.v_compute(this._cy1)

  }

  protected _index_data(index: SpatialIndex): void {
    const {data_size, _x0, _y0, _x1, _y1, _cx0, _cy0, _cx1, _cy1} = this

    for (let i = 0; i < data_size; i++) {
      const x0_i = _x0[i]
      const y0_i = _y0[i]
      const x1_i = _x1[i]
      const y1_i = _y1[i]
      const cx0_i = _cx0[i]
      const cy0_i = _cy0[i]
      const cx1_i = _cx1[i]
      const cy1_i = _cy1[i]

      if (isNaN(x0_i + x1_i + y0_i + y1_i + cx0_i + cy0_i + cx1_i + cy1_i))
        index.add_empty()
      else {
        const [x0, y0, x1, y1] = _cbb(x0_i, y0_i, x1_i, y1_i, cx0_i, cy0_i, cx1_i, cy1_i)
        index.add(x0, y0, x1, y1)
      }
    }
  }

  protected _render(ctx: Context2d, indices: number[], data? : PickData): void {
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

  draw_legend_for_index(ctx: Context2d, {x0, y0, x1, y1}: Rect, index: number): void {
    const len = index + 1

    let sx0 = new Float64Array(len)
    let sy0 = new Float64Array(len)
    let scx0 = new Float64Array(len)
    let scx1 = new Float64Array(len)
    let scy0 = new Float64Array(len)
    let scy1 = new Float64Array(len)
    const [xy0_offset, cx_offset, cy_offset] = _generate_offsets(
        Math.min(Math.abs(x1 - x0), Math.abs(y1 - y0)) * 0.3
    );
    [sx0[index], sy0[index], scx0[index], scx1[index], scy0[index], scy1[index]] = _convert_to_bezier(
        (x0 + x1) / 2, (y0 + y1) / 2, 0, xy0_offset, cx_offset, cy_offset
    );
    const sx1 = sx0;
    const sy1 = sy0;
    this._render(ctx, [index], {sx0, sy0, sx1, sy1, scx0, scx1, scy0, scy1} as any)
  }

  scenterxy(): [number, number] {
    throw new Error(`${this}.scenterxy() is not implemented`)
  }
}

export namespace Pick {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Glyph.Props & {
    x: p.CoordinateSpec
    y: p.CoordinateSpec
    rot: p.AngleSpec
    radius: p.NullDistanceSpec
  } & Mixins

  export type Mixins = LineVector & FillVector

  export type Visuals = Glyph.Visuals & {line: visuals.LineVector, fill: visuals.FillVector}
}

export interface Pick extends Pick.Attrs {}

export class Pick extends Glyph {
  properties: Pick.Props
  __view_type__: PickView

  constructor(attrs?: Partial<Pick.Attrs>) {
    super(attrs)
  }

  __module__ = "ptplot.models.pick"

  static init_Pick(): void {
    this.prototype.default_view = PickView

    this.define<Pick.Props>(({}) => ({
      x:  [ p.XCoordinateSpec, {field: "x"} ],
      y:  [ p.YCoordinateSpec, {field: "y"} ],
      rot:  [ p.AngleSpec, {field: "rot"} ],
      radius: [p.NullDistanceSpec, 1]
    }))
    this.mixins<Pick.Mixins>([FillVector, LineVector])
  }
}