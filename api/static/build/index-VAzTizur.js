var qr = Object.defineProperty;
var zr = (r, e, t) => e in r ? qr(r, e, { enumerable: !0, configurable: !0, writable: !0, value: t }) : r[e] = t;
var Ae = (r, e, t) => zr(r, typeof e != "symbol" ? e + "" : e, t);
function q() {
}
function rr(r) {
  return r();
}
function ds() {
  return /* @__PURE__ */ Object.create(null);
}
function ve(r) {
  r.forEach(rr);
}
function rs(r) {
  return typeof r == "function";
}
function ge(r, e) {
  return r != r ? e == e : r !== e || r && typeof r == "object" || typeof r == "function";
}
let bt;
function zt(r, e) {
  return r === e ? !0 : (bt || (bt = document.createElement("a")), bt.href = e, r === bt.href);
}
function xr(r) {
  return Object.keys(r).length === 0;
}
function nr(r, ...e) {
  if (r == null) {
    for (const s of e)
      s(void 0);
    return q;
  }
  const t = r.subscribe(...e);
  return t.unsubscribe ? () => t.unsubscribe() : t;
}
function Pe(r, e, t) {
  r.$$.on_destroy.push(nr(e, t));
}
const Jr = typeof window < "u" ? window : typeof globalThis < "u" ? globalThis : (
  // @ts-ignore Node typings have this
  global
);
let Rt = !1;
function Kr() {
  Rt = !0;
}
function Yr() {
  Rt = !1;
}
function Xr(r, e, t, s) {
  for (; r < e; ) {
    const n = r + (e - r >> 1);
    t(n) <= s ? r = n + 1 : e = n;
  }
  return r;
}
function Qr(r) {
  if (r.hydrate_init) return;
  r.hydrate_init = !0;
  let e = (
    /** @type {ArrayLike<NodeEx2>} */
    r.childNodes
  );
  if (r.nodeName === "HEAD") {
    const o = [];
    for (let c = 0; c < e.length; c++) {
      const u = e[c];
      u.claim_order !== void 0 && o.push(u);
    }
    e = o;
  }
  const t = new Int32Array(e.length + 1), s = new Int32Array(e.length);
  t[0] = -1;
  let n = 0;
  for (let o = 0; o < e.length; o++) {
    const c = e[o].claim_order, u = (n > 0 && e[t[n]].claim_order <= c ? n + 1 : Xr(1, n, (d) => e[t[d]].claim_order, c)) - 1;
    s[o] = t[u] + 1;
    const h = u + 1;
    t[h] = o, n = Math.max(h, n);
  }
  const i = [], a = [];
  let l = e.length - 1;
  for (let o = t[n] + 1; o != 0; o = s[o - 1]) {
    for (i.push(e[o - 1]); l >= o; l--)
      a.push(e[l]);
    l--;
  }
  for (; l >= 0; l--)
    a.push(e[l]);
  i.reverse(), a.sort((o, c) => o.claim_order - c.claim_order);
  for (let o = 0, c = 0; o < a.length; o++) {
    for (; c < i.length && a[o].claim_order >= i[c].claim_order; )
      c++;
    const u = c < i.length ? i[c] : null;
    r.insertBefore(a[o], u);
  }
}
function f(r, e) {
  if (Rt) {
    for (Qr(r), (r.actual_end_child === void 0 || r.actual_end_child !== null && r.actual_end_child.parentNode !== r) && (r.actual_end_child = r.firstChild); r.actual_end_child !== null && r.actual_end_child.claim_order === void 0; )
      r.actual_end_child = r.actual_end_child.nextSibling;
    e !== r.actual_end_child ? (e.claim_order !== void 0 || e.parentNode !== r) && r.insertBefore(e, r.actual_end_child) : r.actual_end_child = e.nextSibling;
  } else (e.parentNode !== r || e.nextSibling !== null) && r.appendChild(e);
}
function Zr(r, e, t) {
  r.insertBefore(e, t || null);
}
function L(r, e, t) {
  Rt && !t ? f(r, e) : (e.parentNode !== r || e.nextSibling != t) && r.insertBefore(e, t || null);
}
function E(r) {
  r.parentNode && r.parentNode.removeChild(r);
}
function ns(r, e) {
  for (let t = 0; t < r.length; t += 1)
    r[t] && r[t].d(e);
}
function m(r) {
  return document.createElement(r);
}
function en(r) {
  return document.createElementNS("http://www.w3.org/2000/svg", r);
}
function k(r) {
  return document.createTextNode(r);
}
function T() {
  return k(" ");
}
function Le() {
  return k("");
}
function re(r, e, t, s) {
  return r.addEventListener(e, t, s), () => r.removeEventListener(e, t, s);
}
function ir(r) {
  return function(e) {
    return e.preventDefault(), r.call(this, e);
  };
}
function g(r, e, t) {
  t == null ? r.removeAttribute(e) : r.getAttribute(e) !== t && r.setAttribute(e, t);
}
function Y(r) {
  return r.dataset.svelteH;
}
function I(r) {
  return Array.from(r.childNodes);
}
function ar(r) {
  r.claim_info === void 0 && (r.claim_info = { last_index: 0, total_claimed: 0 });
}
function or(r, e, t, s, n = !1) {
  ar(r);
  const i = (() => {
    for (let a = r.claim_info.last_index; a < r.length; a++) {
      const l = r[a];
      if (e(l)) {
        const o = t(l);
        return o === void 0 ? r.splice(a, 1) : r[a] = o, n || (r.claim_info.last_index = a), l;
      }
    }
    for (let a = r.claim_info.last_index - 1; a >= 0; a--) {
      const l = r[a];
      if (e(l)) {
        const o = t(l);
        return o === void 0 ? r.splice(a, 1) : r[a] = o, n ? o === void 0 && r.claim_info.last_index-- : r.claim_info.last_index = a, l;
      }
    }
    return s();
  })();
  return i.claim_order = r.claim_info.total_claimed, r.claim_info.total_claimed += 1, i;
}
function tn(r, e, t, s) {
  return or(
    r,
    /** @returns {node is Element | SVGElement} */
    (n) => n.nodeName === e,
    /** @param {Element} node */
    (n) => {
      const i = [];
      for (let a = 0; a < n.attributes.length; a++) {
        const l = n.attributes[a];
        t[l.name] || i.push(l.name);
      }
      i.forEach((a) => n.removeAttribute(a));
    },
    () => s(e)
  );
}
function b(r, e, t) {
  return tn(r, e, t, m);
}
function P(r, e) {
  return or(
    r,
    /** @returns {node is Text} */
    (t) => t.nodeType === 3,
    /** @param {Text} node */
    (t) => {
      const s = "" + e;
      if (t.data.startsWith(s)) {
        if (t.data.length !== s.length)
          return t.splitText(s.length);
      } else
        t.data = s;
    },
    () => k(e),
    !0
    // Text nodes should not update last index since it is likely not worth it to eliminate an increasing subsequence of actual elements
  );
}
function R(r) {
  return P(r, " ");
}
function fs(r, e, t) {
  for (let s = t; s < r.length; s += 1) {
    const n = r[s];
    if (n.nodeType === 8 && n.textContent.trim() === e)
      return s;
  }
  return -1;
}
function sn(r, e) {
  const t = fs(r, "HTML_TAG_START", 0), s = fs(r, "HTML_TAG_END", t + 1);
  if (t === -1 || s === -1)
    return new Ot(e);
  ar(r);
  const n = r.splice(t, s - t + 1);
  E(n[0]), E(n[n.length - 1]);
  const i = n.slice(1, n.length - 1);
  if (i.length === 0)
    return new Ot(e);
  for (const a of i)
    a.claim_order = r.claim_info.total_claimed, r.claim_info.total_claimed += 1;
  return new Ot(e, i);
}
function M(r, e) {
  e = "" + e, r.data !== e && (r.data = /** @type {string} */
  e);
}
function Ie(r, e) {
  r.value = e ?? "";
}
function yt(r, e, t) {
  r.classList.toggle(e, !!t);
}
class rn {
  constructor(e = !1) {
    /**
     * @private
     * @default false
     */
    Ae(this, "is_svg", !1);
    /** parent for creating node */
    Ae(this, "e");
    /** html tag nodes */
    Ae(this, "n");
    /** target */
    Ae(this, "t");
    /** anchor */
    Ae(this, "a");
    this.is_svg = e, this.e = this.n = null;
  }
  /**
   * @param {string} html
   * @returns {void}
   */
  c(e) {
    this.h(e);
  }
  /**
   * @param {string} html
   * @param {HTMLElement | SVGElement} target
   * @param {HTMLElement | SVGElement} anchor
   * @returns {void}
   */
  m(e, t, s = null) {
    this.e || (this.is_svg ? this.e = en(
      /** @type {keyof SVGElementTagNameMap} */
      t.nodeName
    ) : this.e = m(
      /** @type {keyof HTMLElementTagNameMap} */
      t.nodeType === 11 ? "TEMPLATE" : t.nodeName
    ), this.t = t.tagName !== "TEMPLATE" ? t : (
      /** @type {HTMLTemplateElement} */
      t.content
    ), this.c(e)), this.i(s);
  }
  /**
   * @param {string} html
   * @returns {void}
   */
  h(e) {
    this.e.innerHTML = e, this.n = Array.from(
      this.e.nodeName === "TEMPLATE" ? this.e.content.childNodes : this.e.childNodes
    );
  }
  /**
   * @returns {void} */
  i(e) {
    for (let t = 0; t < this.n.length; t += 1)
      Zr(this.t, this.n[t], e);
  }
  /**
   * @param {string} html
   * @returns {void}
   */
  p(e) {
    this.d(), this.h(e), this.i(this.a);
  }
  /**
   * @returns {void} */
  d() {
    this.n.forEach(E);
  }
}
class Ot extends rn {
  constructor(t = !1, s) {
    super(t);
    /** @type {Element[]} hydration claimed nodes */
    Ae(this, "l");
    this.e = this.n = null, this.l = s;
  }
  /**
   * @param {string} html
   * @returns {void}
   */
  c(t) {
    this.l ? this.n = this.l : super.c(t);
  }
  /**
   * @returns {void} */
  i(t) {
    for (let s = 0; s < this.n.length; s += 1)
      L(this.t, this.n[s], t);
  }
}
let _t;
function ht(r) {
  _t = r;
}
function nn() {
  if (!_t) throw new Error("Function called outside component initialization");
  return _t;
}
function De(r) {
  nn().$$.on_mount.push(r);
}
const Xe = [], tt = [];
let Ze = [];
const _s = [], an = /* @__PURE__ */ Promise.resolve();
let xt = !1;
function on() {
  xt || (xt = !0, an.then(lr));
}
function Jt(r) {
  Ze.push(r);
}
const Ft = /* @__PURE__ */ new Set();
let ze = 0;
function lr() {
  if (ze !== 0)
    return;
  const r = _t;
  do {
    try {
      for (; ze < Xe.length; ) {
        const e = Xe[ze];
        ze++, ht(e), ln(e.$$);
      }
    } catch (e) {
      throw Xe.length = 0, ze = 0, e;
    }
    for (ht(null), Xe.length = 0, ze = 0; tt.length; ) tt.pop()();
    for (let e = 0; e < Ze.length; e += 1) {
      const t = Ze[e];
      Ft.has(t) || (Ft.add(t), t());
    }
    Ze.length = 0;
  } while (Xe.length);
  for (; _s.length; )
    _s.pop()();
  xt = !1, Ft.clear(), ht(r);
}
function ln(r) {
  if (r.fragment !== null) {
    r.update(), ve(r.before_update);
    const e = r.dirty;
    r.dirty = [-1], r.fragment && r.fragment.p(r.ctx, e), r.after_update.forEach(Jt);
  }
}
function cn(r) {
  const e = [], t = [];
  Ze.forEach((s) => r.indexOf(s) === -1 ? e.push(s) : t.push(s)), t.forEach((s) => s()), Ze = e;
}
const Ct = /* @__PURE__ */ new Set();
let Fe;
function Ue() {
  Fe = {
    r: 0,
    c: [],
    p: Fe
    // parent group
  };
}
function Ve() {
  Fe.r || ve(Fe.c), Fe = Fe.p;
}
function J(r, e) {
  r && r.i && (Ct.delete(r), r.i(e));
}
function ae(r, e, t, s) {
  if (r && r.o) {
    if (Ct.has(r)) return;
    Ct.add(r), Fe.c.push(() => {
      Ct.delete(r), s && (t && r.d(1), s());
    }), r.o(e);
  } else s && s();
}
function st(r) {
  return (r == null ? void 0 : r.length) !== void 0 ? r : Array.from(r);
}
function pt(r) {
  r && r.c();
}
function Et(r, e) {
  r && r.l(e);
}
function nt(r, e, t) {
  const { fragment: s, after_update: n } = r.$$;
  s && s.m(e, t), Jt(() => {
    const i = r.$$.on_mount.map(rr).filter(rs);
    r.$$.on_destroy ? r.$$.on_destroy.push(...i) : ve(i), r.$$.on_mount = [];
  }), n.forEach(Jt);
}
function it(r, e) {
  const t = r.$$;
  t.fragment !== null && (cn(t.after_update), ve(t.on_destroy), t.fragment && t.fragment.d(e), t.on_destroy = t.fragment = null, t.ctx = []);
}
function un(r, e) {
  r.$$.dirty[0] === -1 && (Xe.push(r), on(), r.$$.dirty.fill(0)), r.$$.dirty[e / 31 | 0] |= 1 << e % 31;
}
function me(r, e, t, s, n, i, a = null, l = [-1]) {
  const o = _t;
  ht(r);
  const c = r.$$ = {
    fragment: null,
    ctx: [],
    // state
    props: i,
    update: q,
    not_equal: n,
    bound: ds(),
    // lifecycle
    on_mount: [],
    on_destroy: [],
    on_disconnect: [],
    before_update: [],
    after_update: [],
    context: new Map(e.context || (o ? o.$$.context : [])),
    // everything else
    callbacks: ds(),
    dirty: l,
    skip_bound: !1,
    root: e.target || o.$$.root
  };
  a && a(c.root);
  let u = !1;
  if (c.ctx = t ? t(r, e.props || {}, (h, d, ..._) => {
    const p = _.length ? _[0] : d;
    return c.ctx && n(c.ctx[h], c.ctx[h] = p) && (!c.skip_bound && c.bound[h] && c.bound[h](p), u && un(r, h)), d;
  }) : [], c.update(), u = !0, ve(c.before_update), c.fragment = s ? s(c.ctx) : !1, e.target) {
    if (e.hydrate) {
      Kr();
      const h = I(e.target);
      c.fragment && c.fragment.l(h), h.forEach(E);
    } else
      c.fragment && c.fragment.c();
    e.intro && J(r.$$.fragment), nt(r, e.target, e.anchor), Yr(), lr();
  }
  ht(o);
}
class be {
  constructor() {
    /**
     * ### PRIVATE API
     *
     * Do not use, may change at any time
     *
     * @type {any}
     */
    Ae(this, "$$");
    /**
     * ### PRIVATE API
     *
     * Do not use, may change at any time
     *
     * @type {any}
     */
    Ae(this, "$$set");
  }
  /** @returns {void} */
  $destroy() {
    it(this, 1), this.$destroy = q;
  }
  /**
   * @template {Extract<keyof Events, string>} K
   * @param {K} type
   * @param {((e: Events[K]) => void) | null | undefined} callback
   * @returns {() => void}
   */
  $on(e, t) {
    if (!rs(t))
      return q;
    const s = this.$$.callbacks[e] || (this.$$.callbacks[e] = []);
    return s.push(t), () => {
      const n = s.indexOf(t);
      n !== -1 && s.splice(n, 1);
    };
  }
  /**
   * @param {Partial<Props>} props
   * @returns {void}
   */
  $set(e) {
    this.$$set && !xr(e) && (this.$$.skip_bound = !0, this.$$set(e), this.$$.skip_bound = !1);
  }
}
const hn = "4";
typeof window < "u" && (window.__svelte || (window.__svelte = { v: /* @__PURE__ */ new Set() })).v.add(hn);
function gs(r) {
  let e, t;
  return {
    c() {
      e = m("div"), t = k(
        /*partOfSpeech*/
        r[1]
      ), this.h();
    },
    l(s) {
      e = b(s, "DIV", { class: !0 });
      var n = I(e);
      t = P(
        n,
        /*partOfSpeech*/
        r[1]
      ), n.forEach(E), this.h();
    },
    h() {
      g(e, "class", "part-of-speech svelte-fjpf9i");
    },
    m(s, n) {
      L(s, e, n), f(e, t);
    },
    p(s, n) {
      n & /*partOfSpeech*/
      2 && M(
        t,
        /*partOfSpeech*/
        s[1]
      );
    },
    d(s) {
      s && E(e);
    }
  };
}
function ps(r) {
  let e, t = (
    /*translations*/
    r[2].join(", ") + ""
  ), s;
  return {
    c() {
      e = m("div"), s = k(t), this.h();
    },
    l(n) {
      e = b(n, "DIV", { class: !0 });
      var i = I(e);
      s = P(i, t), i.forEach(E), this.h();
    },
    h() {
      g(e, "class", "translations svelte-fjpf9i");
    },
    m(n, i) {
      L(n, e, i), f(e, s);
    },
    p(n, i) {
      i & /*translations*/
      4 && t !== (t = /*translations*/
      n[2].join(", ") + "") && M(s, t);
    },
    d(n) {
      n && E(e);
    }
  };
}
function dn(r) {
  let e, t, s, n, i, a, l, o = (
    /*partOfSpeech*/
    r[1] && gs(r)
  ), c = (
    /*translations*/
    r[2] && /*translations*/
    r[2].length > 0 && ps(r)
  );
  return {
    c() {
      e = m("div"), t = m("a"), s = m("div"), n = m("div"), i = k(
        /*lemma*/
        r[0]
      ), a = T(), o && o.c(), l = T(), c && c.c(), this.h();
    },
    l(u) {
      e = b(u, "DIV", { class: !0 });
      var h = I(e);
      t = b(h, "A", { href: !0, class: !0 });
      var d = I(t);
      s = b(d, "DIV", { class: !0 });
      var _ = I(s);
      n = b(_, "DIV", { class: !0 });
      var p = I(n);
      i = P(
        p,
        /*lemma*/
        r[0]
      ), p.forEach(E), a = R(_), o && o.l(_), l = R(_), c && c.l(_), _.forEach(E), d.forEach(E), h.forEach(E), this.h();
    },
    h() {
      g(n, "class", "lemma-text svelte-fjpf9i"), g(s, "class", "lemma-content svelte-fjpf9i"), g(
        t,
        "href",
        /*href*/
        r[3]
      ), g(t, "class", "lemma-link svelte-fjpf9i"), g(e, "class", "mini-lemma svelte-fjpf9i");
    },
    m(u, h) {
      L(u, e, h), f(e, t), f(t, s), f(s, n), f(n, i), f(s, a), o && o.m(s, null), f(s, l), c && c.m(s, null);
    },
    p(u, [h]) {
      h & /*lemma*/
      1 && M(
        i,
        /*lemma*/
        u[0]
      ), /*partOfSpeech*/
      u[1] ? o ? o.p(u, h) : (o = gs(u), o.c(), o.m(s, l)) : o && (o.d(1), o = null), /*translations*/
      u[2] && /*translations*/
      u[2].length > 0 ? c ? c.p(u, h) : (c = ps(u), c.c(), c.m(s, null)) : c && (c.d(1), c = null), h & /*href*/
      8 && g(
        t,
        "href",
        /*href*/
        u[3]
      );
    },
    i: q,
    o: q,
    d(u) {
      u && E(e), o && o.d(), c && c.d();
    }
  };
}
function fn(r, e, t) {
  let { lemma: s } = e, { partOfSpeech: n = "" } = e, { translations: i = [] } = e, { href: a } = e;
  return r.$$set = (l) => {
    "lemma" in l && t(0, s = l.lemma), "partOfSpeech" in l && t(1, n = l.partOfSpeech), "translations" in l && t(2, i = l.translations), "href" in l && t(3, a = l.href);
  }, [s, n, i, a];
}
class kt extends be {
  constructor(e) {
    super(), me(this, e, fn, dn, ge, {
      lemma: 0,
      partOfSpeech: 1,
      translations: 2,
      href: 3
    });
  }
}
function Es(r) {
  let e, t;
  return {
    c() {
      e = m("div"), t = k(
        /*translation*/
        r[1]
      ), this.h();
    },
    l(s) {
      e = b(s, "DIV", { class: !0 });
      var n = I(e);
      t = P(
        n,
        /*translation*/
        r[1]
      ), n.forEach(E), this.h();
    },
    h() {
      g(e, "class", "translation svelte-22sh89");
    },
    m(s, n) {
      L(s, e, n), f(e, t);
    },
    p(s, n) {
      n & /*translation*/
      2 && M(
        t,
        /*translation*/
        s[1]
      );
    },
    d(s) {
      s && E(e);
    }
  };
}
function _n(r) {
  let e, t, s, n, i, a, l = (
    /*translation*/
    r[1] && Es(r)
  );
  return {
    c() {
      e = m("div"), t = m("a"), s = m("div"), n = m("div"), i = k(
        /*phrase*/
        r[0]
      ), a = T(), l && l.c(), this.h();
    },
    l(o) {
      e = b(o, "DIV", { class: !0 });
      var c = I(e);
      t = b(c, "A", { href: !0, class: !0 });
      var u = I(t);
      s = b(u, "DIV", { class: !0 });
      var h = I(s);
      n = b(h, "DIV", { class: !0 });
      var d = I(n);
      i = P(
        d,
        /*phrase*/
        r[0]
      ), d.forEach(E), a = R(h), l && l.l(h), h.forEach(E), u.forEach(E), c.forEach(E), this.h();
    },
    h() {
      g(n, "class", "phrase svelte-22sh89"), g(s, "class", "sentence-content svelte-22sh89"), g(
        t,
        "href",
        /*href*/
        r[2]
      ), g(t, "class", "sentence-link svelte-22sh89"), g(e, "class", "mini-sentence svelte-22sh89");
    },
    m(o, c) {
      L(o, e, c), f(e, t), f(t, s), f(s, n), f(n, i), f(s, a), l && l.m(s, null);
    },
    p(o, [c]) {
      c & /*phrase*/
      1 && M(
        i,
        /*phrase*/
        o[0]
      ), /*translation*/
      o[1] ? l ? l.p(o, c) : (l = Es(o), l.c(), l.m(s, null)) : l && (l.d(1), l = null), c & /*href*/
      4 && g(
        t,
        "href",
        /*href*/
        o[2]
      );
    },
    i: q,
    o: q,
    d(o) {
      o && E(e), l && l.d();
    }
  };
}
function gn(r, e, t) {
  let { phrase: s } = e, { translation: n } = e, { href: i } = e;
  return r.$$set = (a) => {
    "phrase" in a && t(0, s = a.phrase), "translation" in a && t(1, n = a.translation), "href" in a && t(2, i = a.href);
  }, [s, n, i];
}
class cr extends be {
  constructor(e) {
    super(), me(this, e, gn, _n, ge, { phrase: 0, translation: 1, href: 2 });
  }
}
var de = /* @__PURE__ */ ((r) => (r.SYSTEM_VIEWS_HEALTH_CHECK_VW = "SYSTEM_VIEWS_HEALTH_CHECK_VW", r.SYSTEM_VIEWS_ROUTE_TEST_VW = "SYSTEM_VIEWS_ROUTE_TEST_VW", r.AUTH_VIEWS_AUTH_PAGE_VW = "AUTH_VIEWS_AUTH_PAGE_VW", r.AUTH_VIEWS_PROTECTED_PAGE_VW = "AUTH_VIEWS_PROTECTED_PAGE_VW", r.AUTH_VIEWS_PROFILE_PAGE_VW = "AUTH_VIEWS_PROFILE_PAGE_VW", r.AUTH_API_MANAGE_SESSION_API = "AUTH_API_MANAGE_SESSION_API", r.AUTH_API_GET_USER_API = "AUTH_API_GET_USER_API", r.CORE_VIEWS_HOME_VW = "CORE_VIEWS_HOME_VW", r.CORE_VIEWS_LANGUAGES_LIST_VW = "CORE_VIEWS_LANGUAGES_LIST_VW", r.CORE_VIEWS_EXPERIM_VW = "CORE_VIEWS_EXPERIM_VW", r.CORE_VIEWS_FAVICON_VW = "CORE_VIEWS_FAVICON_VW", r.WORDFORM_VIEWS_WORDFORMS_LIST_VW = "WORDFORM_VIEWS_WORDFORMS_LIST_VW", r.WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW = "WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW", r.WORDFORM_VIEWS_DELETE_WORDFORM_VW = "WORDFORM_VIEWS_DELETE_WORDFORM_VW", r.LEMMA_VIEWS_LEMMAS_LIST_VW = "LEMMA_VIEWS_LEMMAS_LIST_VW", r.LEMMA_VIEWS_GET_LEMMA_METADATA_VW = "LEMMA_VIEWS_GET_LEMMA_METADATA_VW", r.LEMMA_VIEWS_DELETE_LEMMA_VW = "LEMMA_VIEWS_DELETE_LEMMA_VW", r.SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VW = "SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VW", r.SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VW = "SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VW", r.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_VW = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_VW", r.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT_VW = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT_VW", r.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS_VW = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS_VW", r.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES_VW = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES_VW", r.SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW = "SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW", r.SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW = "SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW", r.SOURCEFILE_VIEWS_PROCESS_SOURCEFILE_VW = "SOURCEFILE_VIEWS_PROCESS_SOURCEFILE_VW", r.SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO_VW = "SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO_VW", r.SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES_VW = "SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES_VW", r.SOURCEFILE_VIEWS_NEXT_SOURCEFILE_VW = "SOURCEFILE_VIEWS_NEXT_SOURCEFILE_VW", r.SOURCEFILE_VIEWS_PREV_SOURCEFILE_VW = "SOURCEFILE_VIEWS_PREV_SOURCEFILE_VW", r.PHRASE_VIEWS_PHRASES_LIST_VW = "PHRASE_VIEWS_PHRASES_LIST_VW", r.PHRASE_VIEWS_GET_PHRASE_METADATA_VW = "PHRASE_VIEWS_GET_PHRASE_METADATA_VW", r.PHRASE_VIEWS_DELETE_PHRASE_VW = "PHRASE_VIEWS_DELETE_PHRASE_VW", r.SENTENCE_VIEWS_SENTENCES_LIST_VW = "SENTENCE_VIEWS_SENTENCES_LIST_VW", r.SENTENCE_VIEWS_GET_SENTENCE_VW = "SENTENCE_VIEWS_GET_SENTENCE_VW", r.SEARCH_VIEWS_SEARCH_LANDING_VW = "SEARCH_VIEWS_SEARCH_LANDING_VW", r.SEARCH_VIEWS_SEARCH_WORD_VW = "SEARCH_VIEWS_SEARCH_WORD_VW", r.FLASHCARD_VIEWS_STATIC = "FLASHCARD_VIEWS_STATIC", r.FLASHCARD_VIEWS_FLASHCARD_LANDING_VW = "FLASHCARD_VIEWS_FLASHCARD_LANDING_VW", r.FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW = "FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW", r.FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW = "FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW", r.SOURCEDIR_API_CREATE_SOURCEDIR_API = "SOURCEDIR_API_CREATE_SOURCEDIR_API", r.SOURCEDIR_API_DELETE_SOURCEDIR_API = "SOURCEDIR_API_DELETE_SOURCEDIR_API", r.SOURCEDIR_API_UPDATE_SOURCEDIR_LANGUAGE_API = "SOURCEDIR_API_UPDATE_SOURCEDIR_LANGUAGE_API", r.SOURCEDIR_API_RENAME_SOURCEDIR_API = "SOURCEDIR_API_RENAME_SOURCEDIR_API", r.SOURCEDIR_API_UPLOAD_SOURCEDIR_NEW_SOURCEFILE_API = "SOURCEDIR_API_UPLOAD_SOURCEDIR_NEW_SOURCEFILE_API", r.SOURCEDIR_API_UPDATE_SOURCEDIR_DESCRIPTION_API = "SOURCEDIR_API_UPDATE_SOURCEDIR_DESCRIPTION_API", r.WORDFORM_API_WORD_PREVIEW_API = "WORDFORM_API_WORD_PREVIEW_API", r.WORDFORM_API_GET_MP3_API = "WORDFORM_API_GET_MP3_API", r.LEMMA_API_GET_LEMMA_DATA_API = "LEMMA_API_GET_LEMMA_DATA_API", r.PHRASE_API_PHRASE_PREVIEW_API = "PHRASE_API_PHRASE_PREVIEW_API", r.SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API = "SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API", r.SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API = "SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API", r.SOURCEFILE_API_MOVE_SOURCEFILE_API = "SOURCEFILE_API_MOVE_SOURCEFILE_API", r.SOURCEFILE_API_DELETE_SOURCEFILE_API = "SOURCEFILE_API_DELETE_SOURCEFILE_API", r.SOURCEFILE_API_RENAME_SOURCEFILE_API = "SOURCEFILE_API_RENAME_SOURCEFILE_API", r.SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API = "SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API", r.SOURCEFILE_API_ADD_SOURCEFILE_FROM_YOUTUBE_API = "SOURCEFILE_API_ADD_SOURCEFILE_FROM_YOUTUBE_API", r.SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API = "SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API", r.SENTENCE_API_GET_RANDOM_SENTENCE_API = "SENTENCE_API_GET_RANDOM_SENTENCE_API", r.SENTENCE_API_GET_SENTENCE_AUDIO_API = "SENTENCE_API_GET_SENTENCE_AUDIO_API", r.SENTENCE_API_DELETE_SENTENCE_API = "SENTENCE_API_DELETE_SENTENCE_API", r.SENTENCE_API_RENAME_SENTENCE_API = "SENTENCE_API_RENAME_SENTENCE_API", r.SENTENCE_API_GENERATE_SENTENCE_AUDIO_API = "SENTENCE_API_GENERATE_SENTENCE_AUDIO_API", r))(de || {});
const pn = {
  SYSTEM_VIEWS_HEALTH_CHECK_VW: "/sys/health-check",
  SYSTEM_VIEWS_ROUTE_TEST_VW: "/sys/route-test",
  AUTH_VIEWS_AUTH_PAGE_VW: "/auth/",
  AUTH_VIEWS_PROTECTED_PAGE_VW: "/auth/protected",
  AUTH_VIEWS_PROFILE_PAGE_VW: "/auth/profile",
  AUTH_API_MANAGE_SESSION_API: "/api/auth/session",
  AUTH_API_GET_USER_API: "/api/auth/user",
  CORE_VIEWS_HOME_VW: "/",
  CORE_VIEWS_LANGUAGES_LIST_VW: "/lang",
  CORE_VIEWS_EXPERIM_VW: "/experim",
  CORE_VIEWS_FAVICON_VW: "/favicon.ico",
  WORDFORM_VIEWS_WORDFORMS_LIST_VW: "/lang/{target_language_code}/wordforms/",
  WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW: "/lang/{target_language_code}/wordform/{wordform}",
  WORDFORM_VIEWS_DELETE_WORDFORM_VW: "/lang/{target_language_code}/wordform/{wordform}/delete",
  LEMMA_VIEWS_LEMMAS_LIST_VW: "/lang/{target_language_code}/lemmas",
  LEMMA_VIEWS_GET_LEMMA_METADATA_VW: "/lang/{target_language_code}/lemma/{lemma}",
  LEMMA_VIEWS_DELETE_LEMMA_VW: "/lang/{target_language_code}/lemma/{lemma}/delete",
  SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VW: "/lang/{target_language_code}/",
  SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VW: "/lang/{target_language_code}/{sourcedir_slug}",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/text",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/words",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/phrases",
  SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/view",
  SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/download",
  SOURCEFILE_VIEWS_PROCESS_SOURCEFILE_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/process",
  SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/audio",
  SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/sentences",
  SOURCEFILE_VIEWS_NEXT_SOURCEFILE_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/next",
  SOURCEFILE_VIEWS_PREV_SOURCEFILE_VW: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/prev",
  PHRASE_VIEWS_PHRASES_LIST_VW: "/lang/{target_language_code}/phrases",
  PHRASE_VIEWS_GET_PHRASE_METADATA_VW: "/lang/{target_language_code}/phrases/{slug}",
  PHRASE_VIEWS_DELETE_PHRASE_VW: "/lang/{target_language_code}/phrases/{slug}/delete",
  SENTENCE_VIEWS_SENTENCES_LIST_VW: "/lang/{target_language_code}/sentences",
  SENTENCE_VIEWS_GET_SENTENCE_VW: "/lang/{target_language_code}/sentence/{slug}",
  SEARCH_VIEWS_SEARCH_LANDING_VW: "/lang/{target_language_code}/search",
  SEARCH_VIEWS_SEARCH_WORD_VW: "/lang/{target_language_code}/search/{wordform}",
  FLASHCARD_VIEWS_STATIC: "/lang/build/{filename}",
  FLASHCARD_VIEWS_FLASHCARD_LANDING_VW: "/lang/{target_language_code}/flashcards",
  FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW: "/lang/{target_language_code}/flashcards/sentence/{slug}",
  FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW: "/lang/{target_language_code}/flashcards/random",
  SOURCEDIR_API_CREATE_SOURCEDIR_API: "/api/lang/sourcedir/{target_language_code}",
  SOURCEDIR_API_DELETE_SOURCEDIR_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}",
  SOURCEDIR_API_UPDATE_SOURCEDIR_LANGUAGE_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}/language",
  SOURCEDIR_API_RENAME_SOURCEDIR_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}/rename",
  SOURCEDIR_API_UPLOAD_SOURCEDIR_NEW_SOURCEFILE_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}/upload",
  SOURCEDIR_API_UPDATE_SOURCEDIR_DESCRIPTION_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}/update_description",
  WORDFORM_API_WORD_PREVIEW_API: "/api/lang/word/{target_language_code}/{word}/preview",
  WORDFORM_API_GET_MP3_API: "/api/lang/word/{target_language_code}/{word}/mp3",
  LEMMA_API_GET_LEMMA_DATA_API: "/api/lang/lemma/{target_language_code}/{lemma}/data",
  PHRASE_API_PHRASE_PREVIEW_API: "/api/lang/phrase/{target_language_code}/preview/{phrase}",
  SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/process_individual",
  SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/update_description",
  SOURCEFILE_API_MOVE_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/move",
  SOURCEFILE_API_DELETE_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}",
  SOURCEFILE_API_RENAME_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/rename",
  SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/create_from_text",
  SOURCEFILE_API_ADD_SOURCEFILE_FROM_YOUTUBE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/youtube",
  SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/generate_audio",
  SENTENCE_API_GET_RANDOM_SENTENCE_API: "/api/lang/sentence/{target_language_code}/random",
  SENTENCE_API_GET_SENTENCE_AUDIO_API: "/api/lang/sentence/{target_language_code}/{sentence_id}/audio",
  SENTENCE_API_DELETE_SENTENCE_API: "/api/lang/sentence/{target_language_code}/{slug}",
  SENTENCE_API_RENAME_SENTENCE_API: "/api/lang/sentence/{target_language_code}/{slug}/rename",
  SENTENCE_API_GENERATE_SENTENCE_AUDIO_API: "/api/lang/sentence/{target_language_code}/{slug}/generate_audio"
};
function _e(r, e) {
  let t = pn[r];
  return Object.entries(e).forEach(([s, n]) => {
    t = t.replace(`{${s}}`, encodeURIComponent(String(n)));
  }), t;
}
function vs(r) {
  let e, t, s;
  return {
    c() {
      e = m("span"), t = k("- "), s = k(
        /*translation*/
        r[1]
      ), this.h();
    },
    l(n) {
      e = b(n, "SPAN", { class: !0 });
      var i = I(e);
      t = P(i, "- "), s = P(
        i,
        /*translation*/
        r[1]
      ), i.forEach(E), this.h();
    },
    h() {
      g(e, "class", "translation svelte-1g03yzz");
    },
    m(n, i) {
      L(n, e, i), f(e, t), f(e, s);
    },
    p(n, i) {
      i & /*translation*/
      2 && M(
        s,
        /*translation*/
        n[1]
      );
    },
    d(n) {
      n && E(e);
    }
  };
}
function ms(r) {
  let e, t, s, n;
  return {
    c() {
      e = m("span"), t = k("("), s = k(
        /*notes*/
        r[3]
      ), n = k(")"), this.h();
    },
    l(i) {
      e = b(i, "SPAN", { class: !0 });
      var a = I(e);
      t = P(a, "("), s = P(
        a,
        /*notes*/
        r[3]
      ), n = P(a, ")"), a.forEach(E), this.h();
    },
    h() {
      g(e, "class", "notes svelte-1g03yzz");
    },
    m(i, a) {
      L(i, e, a), f(e, t), f(e, s), f(e, n);
    },
    p(i, a) {
      a & /*notes*/
      8 && M(
        s,
        /*notes*/
        i[3]
      );
    },
    d(i) {
      i && E(e);
    }
  };
}
function En(r) {
  let e, t, s, n, i, a, l, o = (
    /*translation*/
    r[1] && vs(r)
  ), c = (
    /*notes*/
    r[3] && ms(r)
  );
  return {
    c() {
      e = m("div"), t = m("a"), s = m("div"), n = m("span"), i = k(
        /*wordform*/
        r[0]
      ), a = T(), o && o.c(), l = T(), c && c.c(), this.h();
    },
    l(u) {
      e = b(u, "DIV", { class: !0 });
      var h = I(e);
      t = b(h, "A", { href: !0, class: !0 });
      var d = I(t);
      s = b(d, "DIV", { class: !0 });
      var _ = I(s);
      n = b(_, "SPAN", { class: !0 });
      var p = I(n);
      i = P(
        p,
        /*wordform*/
        r[0]
      ), p.forEach(E), a = R(_), o && o.l(_), l = R(_), c && c.l(_), _.forEach(E), d.forEach(E), h.forEach(E), this.h();
    },
    h() {
      g(n, "class", "wordform svelte-1g03yzz"), g(s, "class", "wordform-content svelte-1g03yzz"), g(
        t,
        "href",
        /*href*/
        r[2]
      ), g(t, "class", "wordform-link svelte-1g03yzz"), g(e, "class", "mini-wordform svelte-1g03yzz");
    },
    m(u, h) {
      L(u, e, h), f(e, t), f(t, s), f(s, n), f(n, i), f(s, a), o && o.m(s, null), f(s, l), c && c.m(s, null), r[5](t);
    },
    p(u, [h]) {
      h & /*wordform*/
      1 && M(
        i,
        /*wordform*/
        u[0]
      ), /*translation*/
      u[1] ? o ? o.p(u, h) : (o = vs(u), o.c(), o.m(s, l)) : o && (o.d(1), o = null), /*notes*/
      u[3] ? c ? c.p(u, h) : (c = ms(u), c.c(), c.m(s, null)) : c && (c.d(1), c = null), h & /*href*/
      4 && g(
        t,
        "href",
        /*href*/
        u[2]
      );
    },
    i: q,
    o: q,
    d(u) {
      u && E(e), o && o.d(), c && c.d(), r[5](null);
    }
  };
}
function vn(r, e, t) {
  let { wordform: s } = e, { translation: n = null } = e, { href: i } = e, { notes: a = null } = e, l;
  De(() => {
    if (console.log("MiniWordform component mounted!", { wordform: s, href: i }), !window.tippy) {
      console.error("Tippy.js is not loaded! This will cause errors.");
      return;
    }
    const c = i.split("/"), u = c[1] === "lang" ? c[2] : c[1];
    console.log("Extracted language code:", u), window.tippy(l, {
      content: "Loading...",
      allowHTML: !0,
      theme: "light",
      placement: "bottom",
      touch: !0,
      touchHold: !0,
      interactive: !0,
      appendTo: document.body,
      maxWidth: 300,
      delay: [200, 0],
      onShow(h) {
        document.querySelectorAll("[data-tippy-root]").forEach((_) => {
          const p = _._tippy;
          p && p !== h && p.hide();
        }), console.log(`Fetching preview for word: "${s}" in language: ${u}`);
        const d = _e(de.WORDFORM_API_WORD_PREVIEW_API, {
          target_language_code: u,
          word: s
        });
        fetch(d).then((_) => {
          if (!_.ok)
            throw new Error(`API request failed: ${_.status}`);
          return _.json();
        }).then((_) => {
          console.log(`Preview data for "${s}":`, _), h.setContent(`
              <h4>${_.lemma}</h4>
              ${_.translation ? `<p class="translation">Translation: ${_.translation}</p>` : ""}
              ${_.etymology ? `<p class="etymology">Etymology: ${_.etymology}</p>` : ""}
            `);
        }).catch((_) => {
          console.error(`Error fetching preview for "${s}":`, _), h.setContent("Error loading preview");
        });
      }
    });
  });
  function o(c) {
    tt[c ? "unshift" : "push"](() => {
      l = c, t(4, l);
    });
  }
  return r.$$set = (c) => {
    "wordform" in c && t(0, s = c.wordform), "translation" in c && t(1, n = c.translation), "href" in c && t(2, i = c.href), "notes" in c && t(3, a = c.notes);
  }, [s, n, i, a, l, o];
}
class is extends be {
  constructor(e) {
    super(), me(this, e, vn, En, ge, {
      wordform: 0,
      translation: 1,
      href: 2,
      notes: 3
    });
  }
}
function bs(r, e, t) {
  const s = r.slice();
  return s[3] = e[t], s[5] = t, s;
}
function mn(r) {
  let e, t, s;
  return {
    c() {
      e = m("p"), t = m("em"), s = k(
        /*emptyMessage*/
        r[0]
      ), this.h();
    },
    l(n) {
      e = b(n, "P", { class: !0 });
      var i = I(e);
      t = b(i, "EM", {});
      var a = I(t);
      s = P(
        a,
        /*emptyMessage*/
        r[0]
      ), a.forEach(E), i.forEach(E), this.h();
    },
    h() {
      g(e, "class", "no-entries svelte-1koupvg");
    },
    m(n, i) {
      L(n, e, i), f(e, t), f(t, s);
    },
    p(n, i) {
      i & /*emptyMessage*/
      1 && M(
        s,
        /*emptyMessage*/
        n[0]
      );
    },
    i: q,
    o: q,
    d(n) {
      n && E(e);
    }
  };
}
function bn(r) {
  let e, t, s = st(
    /*sortedWordforms*/
    r[1]
  ), n = [];
  for (let a = 0; a < s.length; a += 1)
    n[a] = ys(bs(r, s, a));
  const i = (a) => ae(n[a], 1, 1, () => {
    n[a] = null;
  });
  return {
    c() {
      e = m("div");
      for (let a = 0; a < n.length; a += 1)
        n[a].c();
      this.h();
    },
    l(a) {
      e = b(a, "DIV", { class: !0 });
      var l = I(e);
      for (let o = 0; o < n.length; o += 1)
        n[o].l(l);
      l.forEach(E), this.h();
    },
    h() {
      g(e, "class", "wordforms-list svelte-1koupvg");
    },
    m(a, l) {
      L(a, e, l);
      for (let o = 0; o < n.length; o += 1)
        n[o] && n[o].m(e, null);
      t = !0;
    },
    p(a, l) {
      if (l & /*sortedWordforms*/
      2) {
        s = st(
          /*sortedWordforms*/
          a[1]
        );
        let o;
        for (o = 0; o < s.length; o += 1) {
          const c = bs(a, s, o);
          n[o] ? (n[o].p(c, l), J(n[o], 1)) : (n[o] = ys(c), n[o].c(), J(n[o], 1), n[o].m(e, null));
        }
        for (Ue(), o = s.length; o < n.length; o += 1)
          i(o);
        Ve();
      }
    },
    i(a) {
      if (!t) {
        for (let l = 0; l < s.length; l += 1)
          J(n[l]);
        t = !0;
      }
    },
    o(a) {
      n = n.filter(Boolean);
      for (let l = 0; l < n.length; l += 1)
        ae(n[l]);
      t = !1;
    },
    d(a) {
      a && E(e), ns(n, a);
    }
  };
}
function ys(r) {
  let e, t;
  return e = new is({
    props: {
      wordform: (
        /*wordform*/
        r[3].wordform
      ),
      translation: (
        /*wordform*/
        r[3].translation
      ),
      href: (
        /*wordform*/
        r[3].href
      ),
      notes: (
        /*wordform*/
        r[3].notes || null
      )
    }
  }), {
    c() {
      pt(e.$$.fragment);
    },
    l(s) {
      Et(e.$$.fragment, s);
    },
    m(s, n) {
      nt(e, s, n), t = !0;
    },
    p(s, n) {
      const i = {};
      n & /*sortedWordforms*/
      2 && (i.wordform = /*wordform*/
      s[3].wordform), n & /*sortedWordforms*/
      2 && (i.translation = /*wordform*/
      s[3].translation), n & /*sortedWordforms*/
      2 && (i.href = /*wordform*/
      s[3].href), n & /*sortedWordforms*/
      2 && (i.notes = /*wordform*/
      s[3].notes || null), e.$set(i);
    },
    i(s) {
      t || (J(e.$$.fragment, s), t = !0);
    },
    o(s) {
      ae(e.$$.fragment, s), t = !1;
    },
    d(s) {
      it(e, s);
    }
  };
}
function yn(r) {
  let e, t, s, n;
  const i = [bn, mn], a = [];
  function l(o, c) {
    return (
      /*sortedWordforms*/
      o[1].length > 0 ? 0 : 1
    );
  }
  return e = l(r), t = a[e] = i[e](r), {
    c() {
      t.c(), s = Le();
    },
    l(o) {
      t.l(o), s = Le();
    },
    m(o, c) {
      a[e].m(o, c), L(o, s, c), n = !0;
    },
    p(o, [c]) {
      let u = e;
      e = l(o), e === u ? a[e].p(o, c) : (Ue(), ae(a[u], 1, 1, () => {
        a[u] = null;
      }), Ve(), t = a[e], t ? t.p(o, c) : (t = a[e] = i[e](o), t.c()), J(t, 1), t.m(s.parentNode, s));
    },
    i(o) {
      n || (J(t), n = !0);
    },
    o(o) {
      ae(t), n = !1;
    },
    d(o) {
      o && E(s), a[e].d(o);
    }
  };
}
function wn(r, e, t) {
  let s, { wordforms: n = [] } = e, { emptyMessage: i = "No words found" } = e;
  return De(() => {
    console.log("MiniWordformList component mounted!", { wordformsCount: n.length });
  }), r.$$set = (a) => {
    "wordforms" in a && t(2, n = a.wordforms), "emptyMessage" in a && t(0, i = a.emptyMessage);
  }, r.$$.update = () => {
    r.$$.dirty & /*wordforms*/
    4 && t(1, s = [...n].sort((a, l) => a.ordering !== void 0 && l.ordering !== void 0 ? a.ordering - l.ordering : 0));
  }, [i, s, n];
}
class ur extends be {
  constructor(e) {
    super(), me(this, e, wn, yn, ge, { wordforms: 2, emptyMessage: 0 });
  }
}
function ws(r) {
  let e, t, s = (
    /*translations*/
    r[1].join(", ") + ""
  ), n;
  return {
    c() {
      e = m("span"), t = k("- "), n = k(s), this.h();
    },
    l(i) {
      e = b(i, "SPAN", { class: !0 });
      var a = I(e);
      t = P(a, "- "), n = P(a, s), a.forEach(E), this.h();
    },
    h() {
      g(e, "class", "translation svelte-z4avom");
    },
    m(i, a) {
      L(i, e, a), f(e, t), f(e, n);
    },
    p(i, a) {
      a & /*translations*/
      2 && s !== (s = /*translations*/
      i[1].join(", ") + "") && M(n, s);
    },
    d(i) {
      i && E(e);
    }
  };
}
function Ss(r) {
  let e, t;
  return {
    c() {
      e = m("span"), t = k(
        /*part_of_speech*/
        r[4]
      ), this.h();
    },
    l(s) {
      e = b(s, "SPAN", { class: !0 });
      var n = I(e);
      t = P(
        n,
        /*part_of_speech*/
        r[4]
      ), n.forEach(E), this.h();
    },
    h() {
      g(e, "class", "part-of-speech svelte-z4avom");
    },
    m(s, n) {
      L(s, e, n), f(e, t);
    },
    p(s, n) {
      n & /*part_of_speech*/
      16 && M(
        t,
        /*part_of_speech*/
        s[4]
      );
    },
    d(s) {
      s && E(e);
    }
  };
}
function Is(r) {
  let e, t, s, n;
  return {
    c() {
      e = m("span"), t = k("("), s = k(
        /*notes*/
        r[3]
      ), n = k(")"), this.h();
    },
    l(i) {
      e = b(i, "SPAN", { class: !0 });
      var a = I(e);
      t = P(a, "("), s = P(
        a,
        /*notes*/
        r[3]
      ), n = P(a, ")"), a.forEach(E), this.h();
    },
    h() {
      g(e, "class", "notes svelte-z4avom");
    },
    m(i, a) {
      L(i, e, a), f(e, t), f(e, s), f(e, n);
    },
    p(i, a) {
      a & /*notes*/
      8 && M(
        s,
        /*notes*/
        i[3]
      );
    },
    d(i) {
      i && E(e);
    }
  };
}
function Sn(r) {
  let e, t, s, n, i, a, l, o, c = (
    /*translations*/
    r[1] && /*translations*/
    r[1].length > 0 && ws(r)
  ), u = (
    /*part_of_speech*/
    r[4] && Ss(r)
  ), h = (
    /*notes*/
    r[3] && Is(r)
  );
  return {
    c() {
      e = m("div"), t = m("a"), s = m("div"), n = m("span"), i = k(
        /*phrase*/
        r[0]
      ), a = T(), c && c.c(), l = T(), u && u.c(), o = T(), h && h.c(), this.h();
    },
    l(d) {
      e = b(d, "DIV", { class: !0 });
      var _ = I(e);
      t = b(_, "A", { href: !0, class: !0 });
      var p = I(t);
      s = b(p, "DIV", { class: !0 });
      var v = I(s);
      n = b(v, "SPAN", { class: !0 });
      var w = I(n);
      i = P(
        w,
        /*phrase*/
        r[0]
      ), w.forEach(E), a = R(v), c && c.l(v), l = R(v), u && u.l(v), o = R(v), h && h.l(v), v.forEach(E), p.forEach(E), _.forEach(E), this.h();
    },
    h() {
      g(n, "class", "phrase svelte-z4avom"), g(s, "class", "phrase-content svelte-z4avom"), g(
        t,
        "href",
        /*href*/
        r[2]
      ), g(t, "class", "phrase-link svelte-z4avom"), g(e, "class", "mini-phrase svelte-z4avom");
    },
    m(d, _) {
      L(d, e, _), f(e, t), f(t, s), f(s, n), f(n, i), f(s, a), c && c.m(s, null), f(s, l), u && u.m(s, null), f(s, o), h && h.m(s, null), r[6](t);
    },
    p(d, [_]) {
      _ & /*phrase*/
      1 && M(
        i,
        /*phrase*/
        d[0]
      ), /*translations*/
      d[1] && /*translations*/
      d[1].length > 0 ? c ? c.p(d, _) : (c = ws(d), c.c(), c.m(s, l)) : c && (c.d(1), c = null), /*part_of_speech*/
      d[4] ? u ? u.p(d, _) : (u = Ss(d), u.c(), u.m(s, o)) : u && (u.d(1), u = null), /*notes*/
      d[3] ? h ? h.p(d, _) : (h = Is(d), h.c(), h.m(s, null)) : h && (h.d(1), h = null), _ & /*href*/
      4 && g(
        t,
        "href",
        /*href*/
        d[2]
      );
    },
    i: q,
    o: q,
    d(d) {
      d && E(e), c && c.d(), u && u.d(), h && h.d(), r[6](null);
    }
  };
}
function In(r, e, t) {
  let { phrase: s } = e, { translations: n = null } = e, { href: i } = e, { notes: a = null } = e, { part_of_speech: l = null } = e, o;
  De(() => {
    console.log("MiniPhrase component mounted!", { phrase: s, href: i });
  });
  function c(u) {
    tt[u ? "unshift" : "push"](() => {
      o = u, t(5, o);
    });
  }
  return r.$$set = (u) => {
    "phrase" in u && t(0, s = u.phrase), "translations" in u && t(1, n = u.translations), "href" in u && t(2, i = u.href), "notes" in u && t(3, a = u.notes), "part_of_speech" in u && t(4, l = u.part_of_speech);
  }, [s, n, i, a, l, o, c];
}
class hr extends be {
  constructor(e) {
    super(), me(this, e, In, Sn, ge, {
      phrase: 0,
      translations: 1,
      href: 2,
      notes: 3,
      part_of_speech: 4
    });
  }
}
function As(r, e, t) {
  const s = r.slice();
  return s[15] = e[t], s;
}
function Os(r) {
  let e, t, s, n, i = (
    /*metadata*/
    (r[1].created_at ? new Date(
      /*metadata*/
      r[1].created_at
    ).toLocaleString() : "N/A") + ""
  ), a, l, o, c, u, h = (
    /*metadata*/
    (r[1].updated_at ? new Date(
      /*metadata*/
      r[1].updated_at
    ).toLocaleString() : "N/A") + ""
  ), d;
  return {
    c() {
      e = m("div"), t = m("p"), s = k("Created: "), n = m("span"), a = k(i), l = T(), o = m("p"), c = k("Updated: "), u = m("span"), d = k(h), this.h();
    },
    l(_) {
      e = b(_, "DIV", { class: !0 });
      var p = I(e);
      t = b(p, "P", { class: !0 });
      var v = I(t);
      s = P(v, "Created: "), n = b(v, "SPAN", { class: !0 });
      var w = I(n);
      a = P(w, i), w.forEach(E), v.forEach(E), l = R(p), o = b(p, "P", { class: !0 });
      var S = I(o);
      c = P(S, "Updated: "), u = b(S, "SPAN", { class: !0 });
      var A = I(u);
      d = P(A, h), A.forEach(E), S.forEach(E), p.forEach(E), this.h();
    },
    h() {
      g(n, "class", "metadata svelte-lkszyl"), g(t, "class", "is-size-7 has-family-monospace"), g(u, "class", "metadata svelte-lkszyl"), g(o, "class", "is-size-7 has-family-monospace"), g(e, "class", "is-pulled-right has-text-right metadata-box svelte-lkszyl");
    },
    m(_, p) {
      L(_, e, p), f(e, t), f(t, s), f(t, n), f(n, a), f(e, l), f(e, o), f(o, c), f(o, u), f(u, d);
    },
    p(_, p) {
      p & /*metadata*/
      2 && i !== (i = /*metadata*/
      (_[1].created_at ? new Date(
        /*metadata*/
        _[1].created_at
      ).toLocaleString() : "N/A") + "") && M(a, i), p & /*metadata*/
      2 && h !== (h = /*metadata*/
      (_[1].updated_at ? new Date(
        /*metadata*/
        _[1].updated_at
      ).toLocaleString() : "N/A") + "") && M(d, h);
    },
    d(_) {
      _ && E(e);
    }
  };
}
function Cs(r) {
  let e, t = (
    /*sentence*/
    r[0].translation + ""
  ), s;
  return {
    c() {
      e = m("div"), s = k(t), this.h();
    },
    l(n) {
      e = b(n, "DIV", { class: !0 });
      var i = I(e);
      s = P(i, t), i.forEach(E), this.h();
    },
    h() {
      g(e, "class", "english-translation has-text-grey is-italic mb-5 svelte-lkszyl");
    },
    m(n, i) {
      L(n, e, i), f(e, s);
    },
    p(n, i) {
      i & /*sentence*/
      1 && t !== (t = /*sentence*/
      n[0].translation + "") && M(s, t);
    },
    d(n) {
      n && E(e);
    }
  };
}
function An(r) {
  let e, t, s = '<i class="fas fa-volume-up"></i>', n, i, a = (
    /*isGeneratingAudio*/
    r[4] ? "Generating..." : "Generate audio"
  ), l, o, c;
  return {
    c() {
      e = m("button"), t = m("span"), t.innerHTML = s, n = T(), i = m("span"), l = k(a), this.h();
    },
    l(u) {
      e = b(u, "BUTTON", { class: !0 });
      var h = I(e);
      t = b(h, "SPAN", { class: !0, "data-svelte-h": !0 }), Y(t) !== "svelte-16ckn7i" && (t.innerHTML = s), n = R(h), i = b(h, "SPAN", {});
      var d = I(i);
      l = P(d, a), d.forEach(E), h.forEach(E), this.h();
    },
    h() {
      g(t, "class", "icon"), g(e, "class", "button is-primary"), e.disabled = /*isGeneratingAudio*/
      r[4];
    },
    m(u, h) {
      L(u, e, h), f(e, t), f(e, n), f(e, i), f(i, l), o || (c = re(
        e,
        "click",
        /*generateAudio*/
        r[6]
      ), o = !0);
    },
    p(u, h) {
      h & /*isGeneratingAudio*/
      16 && a !== (a = /*isGeneratingAudio*/
      u[4] ? "Generating..." : "Generate audio") && M(l, a), h & /*isGeneratingAudio*/
      16 && (e.disabled = /*isGeneratingAudio*/
      u[4]);
    },
    d(u) {
      u && E(e), o = !1, c();
    }
  };
}
function On(r) {
  let e, t, s, n, i, a, l, o = "0.8x", c, u, h = "0.9x", d, _, p = "1.0x", v, w, S = "1.5x", A, y;
  return {
    c() {
      e = m("div"), t = m("audio"), s = k("Your browser does not support the audio element."), i = T(), a = m("div"), l = m("button"), l.textContent = o, c = T(), u = m("button"), u.textContent = h, d = T(), _ = m("button"), _.textContent = p, v = T(), w = m("button"), w.textContent = S, this.h();
    },
    l(O) {
      e = b(O, "DIV", { class: !0 });
      var C = I(e);
      t = b(C, "AUDIO", { src: !0, class: !0 });
      var D = I(t);
      s = P(D, "Your browser does not support the audio element."), D.forEach(E), i = R(C), a = b(C, "DIV", { class: !0 });
      var F = I(a);
      l = b(F, "BUTTON", { class: !0, "data-svelte-h": !0 }), Y(l) !== "svelte-14987qe" && (l.textContent = o), c = R(F), u = b(F, "BUTTON", { class: !0, "data-svelte-h": !0 }), Y(u) !== "svelte-1q4z4he" && (u.textContent = h), d = R(F), _ = b(F, "BUTTON", { class: !0, "data-svelte-h": !0 }), Y(_) !== "svelte-zlp2ay" && (_.textContent = p), v = R(F), w = b(F, "BUTTON", { class: !0, "data-svelte-h": !0 }), Y(w) !== "svelte-d5tdq6" && (w.textContent = S), F.forEach(E), C.forEach(E), this.h();
    },
    h() {
      t.controls = !0, zt(t.src, n = /*audioUrl*/
      r[8]) || g(t, "src", n), g(t, "class", "audio-player is-fullwidth svelte-lkszyl"), g(l, "class", "button is-small has-family-monospace"), g(u, "class", "button is-small has-family-monospace"), g(_, "class", "button is-small has-family-monospace"), g(w, "class", "button is-small has-family-monospace"), g(a, "class", "buttons has-addons is-centered mt-2"), g(e, "class", "audio-section");
    },
    m(O, C) {
      L(O, e, C), f(e, t), f(t, s), r[9](t), f(e, i), f(e, a), f(a, l), f(a, c), f(a, u), f(a, d), f(a, _), f(a, v), f(a, w), A || (y = [
        re(
          l,
          "click",
          /*click_handler*/
          r[10]
        ),
        re(
          u,
          "click",
          /*click_handler_1*/
          r[11]
        ),
        re(
          _,
          "click",
          /*click_handler_2*/
          r[12]
        ),
        re(
          w,
          "click",
          /*click_handler_3*/
          r[13]
        )
      ], A = !0);
    },
    p: q,
    d(O) {
      O && E(e), r[9](null), A = !1, ve(y);
    }
  };
}
function Ts(r) {
  let e, t, s = "Words", n, i, a, l = st(
    /*sentence*/
    r[0].lemma_words
  ), o = [];
  for (let u = 0; u < l.length; u += 1)
    o[u] = ks(As(r, l, u));
  const c = (u) => ae(o[u], 1, 1, () => {
    o[u] = null;
  });
  return {
    c() {
      e = m("div"), t = m("h3"), t.textContent = s, n = T(), i = m("div");
      for (let u = 0; u < o.length; u += 1)
        o[u].c();
      this.h();
    },
    l(u) {
      e = b(u, "DIV", { class: !0 });
      var h = I(e);
      t = b(h, "H3", { class: !0, "data-svelte-h": !0 }), Y(t) !== "svelte-1b23zca" && (t.textContent = s), n = R(h), i = b(h, "DIV", { class: !0 });
      var d = I(i);
      for (let _ = 0; _ < o.length; _ += 1)
        o[_].l(d);
      d.forEach(E), h.forEach(E), this.h();
    },
    h() {
      g(t, "class", "title is-5"), g(i, "class", "words-list"), g(e, "class", "words-section mt-6 pt-4 border-top svelte-lkszyl");
    },
    m(u, h) {
      L(u, e, h), f(e, t), f(e, n), f(e, i);
      for (let d = 0; d < o.length; d += 1)
        o[d] && o[d].m(i, null);
      a = !0;
    },
    p(u, h) {
      if (h & /*lemmasData, sentence*/
      33) {
        l = st(
          /*sentence*/
          u[0].lemma_words
        );
        let d;
        for (d = 0; d < l.length; d += 1) {
          const _ = As(u, l, d);
          o[d] ? (o[d].p(_, h), J(o[d], 1)) : (o[d] = ks(_), o[d].c(), J(o[d], 1), o[d].m(i, null));
        }
        for (Ue(), d = l.length; d < o.length; d += 1)
          c(d);
        Ve();
      }
    },
    i(u) {
      if (!a) {
        for (let h = 0; h < l.length; h += 1)
          J(o[h]);
        a = !0;
      }
    },
    o(u) {
      o = o.filter(Boolean);
      for (let h = 0; h < o.length; h += 1)
        ae(o[h]);
      a = !1;
    },
    d(u) {
      u && E(e), ns(o, u);
    }
  };
}
function Rs(r) {
  let e, t = "Loading lemma data...";
  return {
    c() {
      e = m("div"), e.textContent = t, this.h();
    },
    l(s) {
      e = b(s, "DIV", { class: !0, "data-svelte-h": !0 }), Y(e) !== "svelte-yn0dt0" && (e.textContent = t), this.h();
    },
    h() {
      g(e, "class", "has-text-grey is-size-7 is-italic ml-3 has-family-monospace");
    },
    m(s, n) {
      L(s, e, n);
    },
    d(s) {
      s && E(e);
    }
  };
}
function ks(r) {
  var l, o, c;
  let e, t, s, n, i;
  t = new kt({
    props: {
      lemma: (
        /*lemma*/
        r[15]
      ),
      partOfSpeech: (
        /*lemmasData*/
        ((l = r[5][
          /*lemma*/
          r[15]
        ]) == null ? void 0 : l.part_of_speech) || ""
      ),
      translations: (
        /*lemmasData*/
        ((o = r[5][
          /*lemma*/
          r[15]
        ]) == null ? void 0 : o.translations) || []
      ),
      href: "/lang/" + /*sentence*/
      r[0].language_code + "/lemma/" + /*lemma*/
      r[15]
    }
  });
  let a = (
    /*lemmasData*/
    ((c = r[5][
      /*lemma*/
      r[15]
    ]) == null ? void 0 : c.isLoading) && Rs()
  );
  return {
    c() {
      e = m("div"), pt(t.$$.fragment), s = T(), a && a.c(), n = T(), this.h();
    },
    l(u) {
      e = b(u, "DIV", { class: !0 });
      var h = I(e);
      Et(t.$$.fragment, h), s = R(h), a && a.l(h), n = R(h), h.forEach(E), this.h();
    },
    h() {
      g(e, "class", "mb-2");
    },
    m(u, h) {
      L(u, e, h), nt(t, e, null), f(e, s), a && a.m(e, null), f(e, n), i = !0;
    },
    p(u, h) {
      var _, p, v;
      const d = {};
      h & /*sentence*/
      1 && (d.lemma = /*lemma*/
      u[15]), h & /*lemmasData, sentence*/
      33 && (d.partOfSpeech = /*lemmasData*/
      ((_ = u[5][
        /*lemma*/
        u[15]
      ]) == null ? void 0 : _.part_of_speech) || ""), h & /*lemmasData, sentence*/
      33 && (d.translations = /*lemmasData*/
      ((p = u[5][
        /*lemma*/
        u[15]
      ]) == null ? void 0 : p.translations) || []), h & /*sentence*/
      1 && (d.href = "/lang/" + /*sentence*/
      u[0].language_code + "/lemma/" + /*lemma*/
      u[15]), t.$set(d), /*lemmasData*/
      (v = u[5][
        /*lemma*/
        u[15]
      ]) != null && v.isLoading ? a || (a = Rs(), a.c(), a.m(e, n)) : a && (a.d(1), a = null);
    },
    i(u) {
      i || (J(t.$$.fragment, u), i = !0);
    },
    o(u) {
      ae(t.$$.fragment, u), i = !1;
    },
    d(u) {
      u && E(e), it(t), a && a.d();
    }
  };
}
function Cn(r) {
  let e, t, s, n, i, a, l, o = (
    /*enhanced_sentence_text*/
    (r[2] || "<p>No sentence text available</p>") + ""
  ), c, u, h, d, _, p = (
    /*metadata*/
    r[1] && Os(r)
  ), v = (
    /*sentence*/
    r[0].translation && Cs(r)
  );
  function w(O, C) {
    return (
      /*sentence*/
      O[0].has_audio ? On : An
    );
  }
  let S = w(r), A = S(r), y = (
    /*sentence*/
    r[0].lemma_words && Ts(r)
  );
  return {
    c() {
      e = m("div"), t = m("div"), s = m("div"), p && p.c(), n = T(), i = m("div"), a = m("div"), l = new Ot(!1), c = T(), v && v.c(), u = T(), h = m("div"), A.c(), d = T(), y && y.c(), this.h();
    },
    l(O) {
      e = b(O, "DIV", { class: !0 });
      var C = I(e);
      t = b(C, "DIV", { class: !0 });
      var D = I(t);
      s = b(D, "DIV", { class: !0 });
      var F = I(s);
      p && p.l(F), n = R(F), i = b(F, "DIV", { class: !0 });
      var V = I(i);
      a = b(V, "DIV", { class: !0 });
      var W = I(a);
      l = sn(W, !1), W.forEach(E), c = R(V), v && v.l(V), u = R(V), h = b(V, "DIV", { class: !0 });
      var U = I(h);
      A.l(U), U.forEach(E), d = R(V), y && y.l(V), V.forEach(E), F.forEach(E), D.forEach(E), C.forEach(E), this.h();
    },
    h() {
      l.a = null, g(a, "class", "target-lang-text mb-4 svelte-lkszyl"), g(h, "class", "mb-5"), g(i, "class", "content main-content"), g(s, "class", "card-content"), g(t, "class", "card"), g(e, "class", "section sentence-page svelte-lkszyl");
    },
    m(O, C) {
      L(O, e, C), f(e, t), f(t, s), p && p.m(s, null), f(s, n), f(s, i), f(i, a), l.m(o, a), f(i, c), v && v.m(i, null), f(i, u), f(i, h), A.m(h, null), f(i, d), y && y.m(i, null), _ = !0;
    },
    p(O, [C]) {
      /*metadata*/
      O[1] ? p ? p.p(O, C) : (p = Os(O), p.c(), p.m(s, n)) : p && (p.d(1), p = null), (!_ || C & /*enhanced_sentence_text*/
      4) && o !== (o = /*enhanced_sentence_text*/
      (O[2] || "<p>No sentence text available</p>") + "") && l.p(o), /*sentence*/
      O[0].translation ? v ? v.p(O, C) : (v = Cs(O), v.c(), v.m(i, u)) : v && (v.d(1), v = null), S === (S = w(O)) && A ? A.p(O, C) : (A.d(1), A = S(O), A && (A.c(), A.m(h, null))), /*sentence*/
      O[0].lemma_words ? y ? (y.p(O, C), C & /*sentence*/
      1 && J(y, 1)) : (y = Ts(O), y.c(), J(y, 1), y.m(i, null)) : y && (Ue(), ae(y, 1, 1, () => {
        y = null;
      }), Ve());
    },
    i(O) {
      _ || (J(y), _ = !0);
    },
    o(O) {
      ae(y), _ = !1;
    },
    d(O) {
      O && E(e), p && p.d(), v && v.d(), A.d(), y && y.d();
    }
  };
}
function Tn(r, e, t) {
  let { sentence: s } = e, { metadata: n } = e, { enhanced_sentence_text: i } = e, a, l = !1, o = {};
  De(() => {
  }), s.lemma_words && s.lemma_words.forEach((A) => {
    t(
      5,
      o[A] = {
        lemma: A,
        part_of_speech: "",
        translations: [],
        isLoading: !0,
        error: null
      },
      o
    );
  });
  async function c(A) {
    try {
      const y = _e(de.LEMMA_API_GET_LEMMA_DATA_API, {
        target_language_code: s.language_code,
        lemma: A
      }), O = await fetch(y);
      if (!O.ok)
        throw new Error(`Failed to fetch lemma data for ${A}`);
      const C = await O.json();
      t(
        5,
        o[A] = {
          lemma: A,
          part_of_speech: C.part_of_speech || "",
          translations: C.translations || [],
          isLoading: !1,
          error: null
        },
        o
      );
    } catch (y) {
      console.error("Error fetching lemma data:", y), t(
        5,
        o[A] = {
          ...o[A],
          isLoading: !1,
          error: String(y)
        },
        o
      );
    }
  }
  s.lemma_words && s.lemma_words.forEach(c);
  async function u() {
    if (!l) {
      t(4, l = !0);
      try {
        const A = _e(de.SENTENCE_API_GENERATE_SENTENCE_AUDIO_API, {
          target_language_code: s.language_code,
          slug: s.slug
        });
        if (!(await fetch(A, { method: "POST" })).ok) throw new Error("Failed to generate audio");
        window.location.reload();
      } catch (A) {
        console.error("Error generating audio:", A);
      } finally {
        t(4, l = !1);
      }
    }
  }
  function h(A) {
    a && t(3, a.playbackRate = A, a);
  }
  const d = _e(de.SENTENCE_API_GET_SENTENCE_AUDIO_API, {
    target_language_code: s.language_code,
    sentence_id: String(s.id)
  });
  function _(A) {
    tt[A ? "unshift" : "push"](() => {
      a = A, t(3, a);
    });
  }
  const p = () => h(0.8), v = () => h(0.9), w = () => h(1), S = () => h(1.5);
  return r.$$set = (A) => {
    "sentence" in A && t(0, s = A.sentence), "metadata" in A && t(1, n = A.metadata), "enhanced_sentence_text" in A && t(2, i = A.enhanced_sentence_text);
  }, [
    s,
    n,
    i,
    a,
    l,
    o,
    u,
    h,
    d,
    _,
    p,
    v,
    w,
    S
  ];
}
class dr extends be {
  constructor(e) {
    super(), me(this, e, Tn, Cn, ge, {
      sentence: 0,
      metadata: 1,
      enhanced_sentence_text: 2
    });
  }
}
function Rn(r) {
  if (r.stage >= 3)
    return r;
  const e = r.stage + 1;
  return {
    ...r,
    stage: e
  };
}
function kn(r) {
  if (r.stage <= 1)
    return r;
  const e = r.stage - 1;
  return {
    ...r,
    stage: e
  };
}
function Pn(r) {
  switch (r) {
    case 1:
      return {
        left: "Play Audio",
        right: "Show Sentence",
        leftDisabled: !1,
        rightDisabled: !1
      };
    case 2:
      return {
        left: "Play Audio",
        right: "Show Translation",
        leftDisabled: !1,
        rightDisabled: !1
      };
    case 3:
      return {
        left: "Show Sentence",
        right: "Show Translation",
        leftDisabled: !1,
        rightDisabled: !0
      };
    default:
      return {
        left: "Play Audio",
        right: "Next",
        leftDisabled: !1,
        rightDisabled: !1
      };
  }
}
function Ps(r, e, t) {
  const s = r.slice();
  return s[16] = e[t], s;
}
function Ls(r) {
  let e, t = (
    /*state*/
    r[2].error + ""
  ), s;
  return {
    c() {
      e = m("div"), s = k(t), this.h();
    },
    l(n) {
      e = b(n, "DIV", { class: !0 });
      var i = I(e);
      s = P(i, t), i.forEach(E), this.h();
    },
    h() {
      g(e, "class", "error-message svelte-1ee5qgk");
    },
    m(n, i) {
      L(n, e, i), f(e, s);
    },
    p(n, i) {
      i & /*state*/
      4 && t !== (t = /*state*/
      n[2].error + "") && M(s, t);
    },
    d(n) {
      n && E(e);
    }
  };
}
function Ds(r) {
  let e, t, s, n = (
    /*state*/
    r[2].sourceFilter.type === "sourcedir" ? "directory" : "file"
  ), i, a, l, o = (
    /*state*/
    r[2].sourceFilter.slug + ""
  ), c, u, h, d, _;
  return {
    c() {
      e = m("div"), t = m("i"), s = k(`
      Filtered by `), i = k(n), a = k(`: 
      `), l = m("strong"), c = k(o), u = T(), h = m("a"), d = m("i"), this.h();
    },
    l(p) {
      e = b(p, "DIV", { class: !0 });
      var v = I(e);
      t = b(v, "I", { class: !0 }), I(t).forEach(E), s = P(v, `
      Filtered by `), i = P(v, n), a = P(v, `: 
      `), l = b(v, "STRONG", {});
      var w = I(l);
      c = P(w, o), w.forEach(E), u = R(v), h = b(v, "A", { href: !0, class: !0 });
      var S = I(h);
      d = b(S, "I", { class: !0 }), I(d).forEach(E), S.forEach(E), v.forEach(E), this.h();
    },
    h() {
      g(t, "class", "ph-fill ph-filter svelte-1ee5qgk"), g(d, "class", "ph-fill ph-x svelte-1ee5qgk"), g(h, "href", _ = _e(de.FLASHCARD_VIEWS_FLASHCARD_LANDING_VW, {
        target_language_code: (
          /*targetLanguageCode*/
          r[1]
        )
      })), g(h, "class", "clear-filter svelte-1ee5qgk"), g(e, "class", "source-filter-banner svelte-1ee5qgk");
    },
    m(p, v) {
      L(p, e, v), f(e, t), f(e, s), f(e, i), f(e, a), f(e, l), f(l, c), f(e, u), f(e, h), f(h, d);
    },
    p(p, v) {
      v & /*state*/
      4 && n !== (n = /*state*/
      p[2].sourceFilter.type === "sourcedir" ? "directory" : "file") && M(i, n), v & /*state*/
      4 && o !== (o = /*state*/
      p[2].sourceFilter.slug + "") && M(c, o), v & /*targetLanguageCode*/
      2 && _ !== (_ = _e(de.FLASHCARD_VIEWS_FLASHCARD_LANDING_VW, {
        target_language_code: (
          /*targetLanguageCode*/
          p[1]
        )
      })) && g(h, "href", _);
    },
    d(p) {
      p && E(e);
    }
  };
}
function Us(r) {
  let e, t = (
    /*sentence*/
    r[0].text + ""
  ), s;
  return {
    c() {
      e = m("h3"), s = k(t), this.h();
    },
    l(n) {
      e = b(n, "H3", { class: !0 });
      var i = I(e);
      s = P(i, t), i.forEach(E), this.h();
    },
    h() {
      g(e, "class", "sentence-text svelte-1ee5qgk");
    },
    m(n, i) {
      L(n, e, i), f(e, s);
    },
    p(n, i) {
      i & /*sentence*/
      1 && t !== (t = /*sentence*/
      n[0].text + "") && M(s, t);
    },
    d(n) {
      n && E(e);
    }
  };
}
function Vs(r) {
  let e, t = (
    /*sentence*/
    r[0].translation + ""
  ), s, n, i, a, l = (
    /*sentence*/
    r[0].lemmaWords && /*sentence*/
    r[0].lemmaWords.length > 0 && Ws(r)
  );
  return {
    c() {
      e = m("p"), s = k(t), n = T(), l && l.c(), i = Le(), this.h();
    },
    l(o) {
      e = b(o, "P", { class: !0 });
      var c = I(e);
      s = P(c, t), c.forEach(E), n = R(o), l && l.l(o), i = Le(), this.h();
    },
    h() {
      g(e, "class", "translation-text svelte-1ee5qgk");
    },
    m(o, c) {
      L(o, e, c), f(e, s), L(o, n, c), l && l.m(o, c), L(o, i, c), a = !0;
    },
    p(o, c) {
      (!a || c & /*sentence*/
      1) && t !== (t = /*sentence*/
      o[0].translation + "") && M(s, t), /*sentence*/
      o[0].lemmaWords && /*sentence*/
      o[0].lemmaWords.length > 0 ? l ? (l.p(o, c), c & /*sentence*/
      1 && J(l, 1)) : (l = Ws(o), l.c(), J(l, 1), l.m(i.parentNode, i)) : l && (Ue(), ae(l, 1, 1, () => {
        l = null;
      }), Ve());
    },
    i(o) {
      a || (J(l), a = !0);
    },
    o(o) {
      ae(l), a = !1;
    },
    d(o) {
      o && (E(e), E(n), E(i)), l && l.d(o);
    }
  };
}
function Ws(r) {
  let e, t, s = "Vocabulary", n, i, a, l = st(
    /*sentence*/
    r[0].lemmaWords
  ), o = [];
  for (let u = 0; u < l.length; u += 1)
    o[u] = Ns(Ps(r, l, u));
  const c = (u) => ae(o[u], 1, 1, () => {
    o[u] = null;
  });
  return {
    c() {
      e = m("div"), t = m("h3"), t.textContent = s, n = T(), i = m("div");
      for (let u = 0; u < o.length; u += 1)
        o[u].c();
      this.h();
    },
    l(u) {
      e = b(u, "DIV", { class: !0 });
      var h = I(e);
      t = b(h, "H3", { class: !0, "data-svelte-h": !0 }), Y(t) !== "svelte-1imm3z0" && (t.textContent = s), n = R(h), i = b(h, "DIV", { class: !0 });
      var d = I(i);
      for (let _ = 0; _ < o.length; _ += 1)
        o[_].l(d);
      d.forEach(E), h.forEach(E), this.h();
    },
    h() {
      g(t, "class", "svelte-1ee5qgk"), g(i, "class", "words-list svelte-1ee5qgk"), g(e, "class", "words-section svelte-1ee5qgk");
    },
    m(u, h) {
      L(u, e, h), f(e, t), f(e, n), f(e, i);
      for (let d = 0; d < o.length; d += 1)
        o[d] && o[d].m(i, null);
      a = !0;
    },
    p(u, h) {
      if (h & /*lemmasData, sentence, targetLanguageCode*/
      19) {
        l = st(
          /*sentence*/
          u[0].lemmaWords
        );
        let d;
        for (d = 0; d < l.length; d += 1) {
          const _ = Ps(u, l, d);
          o[d] ? (o[d].p(_, h), J(o[d], 1)) : (o[d] = Ns(_), o[d].c(), J(o[d], 1), o[d].m(i, null));
        }
        for (Ue(), d = l.length; d < o.length; d += 1)
          c(d);
        Ve();
      }
    },
    i(u) {
      if (!a) {
        for (let h = 0; h < l.length; h += 1)
          J(o[h]);
        a = !0;
      }
    },
    o(u) {
      o = o.filter(Boolean);
      for (let h = 0; h < o.length; h += 1)
        ae(o[h]);
      a = !1;
    },
    d(u) {
      u && E(e), ns(o, u);
    }
  };
}
function js(r) {
  let e, t = "Loading lemma data...";
  return {
    c() {
      e = m("div"), e.textContent = t, this.h();
    },
    l(s) {
      e = b(s, "DIV", { class: !0, "data-svelte-h": !0 }), Y(e) !== "svelte-iu7ef5" && (e.textContent = t), this.h();
    },
    h() {
      g(e, "class", "loading-indicator svelte-1ee5qgk");
    },
    m(s, n) {
      L(s, e, n);
    },
    d(s) {
      s && E(e);
    }
  };
}
function Ns(r) {
  var a, l, o;
  let e, t, s, n;
  e = new kt({
    props: {
      lemma: (
        /*lemma*/
        r[16]
      ),
      partOfSpeech: (
        /*lemmasData*/
        ((a = r[4][
          /*lemma*/
          r[16]
        ]) == null ? void 0 : a.part_of_speech) || ""
      ),
      translations: (
        /*lemmasData*/
        ((l = r[4][
          /*lemma*/
          r[16]
        ]) == null ? void 0 : l.translations) || []
      ),
      href: _e(de.LEMMA_VIEWS_GET_LEMMA_METADATA_VW, {
        target_language_code: (
          /*targetLanguageCode*/
          r[1]
        ),
        lemma: (
          /*lemma*/
          r[16]
        )
      })
    }
  });
  let i = (
    /*lemmasData*/
    ((o = r[4][
      /*lemma*/
      r[16]
    ]) == null ? void 0 : o.isLoading) && js()
  );
  return {
    c() {
      pt(e.$$.fragment), t = T(), i && i.c(), s = Le();
    },
    l(c) {
      Et(e.$$.fragment, c), t = R(c), i && i.l(c), s = Le();
    },
    m(c, u) {
      nt(e, c, u), L(c, t, u), i && i.m(c, u), L(c, s, u), n = !0;
    },
    p(c, u) {
      var d, _, p;
      const h = {};
      u & /*sentence*/
      1 && (h.lemma = /*lemma*/
      c[16]), u & /*lemmasData, sentence*/
      17 && (h.partOfSpeech = /*lemmasData*/
      ((d = c[4][
        /*lemma*/
        c[16]
      ]) == null ? void 0 : d.part_of_speech) || ""), u & /*lemmasData, sentence*/
      17 && (h.translations = /*lemmasData*/
      ((_ = c[4][
        /*lemma*/
        c[16]
      ]) == null ? void 0 : _.translations) || []), u & /*targetLanguageCode, sentence*/
      3 && (h.href = _e(de.LEMMA_VIEWS_GET_LEMMA_METADATA_VW, {
        target_language_code: (
          /*targetLanguageCode*/
          c[1]
        ),
        lemma: (
          /*lemma*/
          c[16]
        )
      })), e.$set(h), /*lemmasData*/
      (p = c[4][
        /*lemma*/
        c[16]
      ]) != null && p.isLoading ? i || (i = js(), i.c(), i.m(s.parentNode, s)) : i && (i.d(1), i = null);
    },
    i(c) {
      n || (J(e.$$.fragment, c), n = !0);
    },
    o(c) {
      ae(e.$$.fragment, c), n = !1;
    },
    d(c) {
      c && (E(t), E(s)), it(e, c), i && i.d(c);
    }
  };
}
function Ln(r) {
  let e, t, s, n, i, a, l, o, c, u, h, d, _, p, v = (
    /*buttonLabels*/
    r[5].left + ""
  ), w, S, A, y = "(←)", O, C, D, F, V, W, U = (
    /*buttonLabels*/
    r[5].right + ""
  ), se, le, X, ce = "(→)", Q, ne, Z, pe = `<i class="fas fa-forward"></i>
      New Sentence
      <span class="shortcut-hint svelte-1ee5qgk">(Enter)</span>`, H, K, $, j = (
    /*state*/
    r[2].error && Ls(r)
  ), z = (
    /*state*/
    r[2].sourceFilter.type && /*state*/
    r[2].sourceFilter.slug && Ds(r)
  ), ie = (
    /*state*/
    r[2].stage >= 2 && Us(r)
  ), te = (
    /*state*/
    r[2].stage >= 3 && Vs(r)
  );
  return {
    c() {
      e = m("div"), j && j.c(), t = T(), z && z.c(), s = T(), n = m("div"), i = m("audio"), l = T(), ie && ie.c(), o = T(), te && te.c(), c = T(), u = m("div"), h = m("button"), d = m("i"), p = T(), w = k(v), S = T(), A = m("span"), A.textContent = y, C = T(), D = m("button"), F = m("i"), W = T(), se = k(U), le = T(), X = m("span"), X.textContent = ce, ne = T(), Z = m("button"), Z.innerHTML = pe, this.h();
    },
    l(B) {
      e = b(B, "DIV", { class: !0 });
      var x = I(e);
      j && j.l(x), t = R(x), z && z.l(x), s = R(x), n = b(x, "DIV", { class: !0 });
      var $e = I(n);
      i = b($e, "AUDIO", { src: !0, preload: !0 }), I(i).forEach(E), l = R($e), ie && ie.l($e), o = R($e), te && te.l($e), $e.forEach(E), c = R(x), u = b(x, "DIV", { class: !0 });
      var Be = I(u);
      h = b(Be, "BUTTON", { class: !0 });
      var Ge = I(h);
      d = b(Ge, "I", { class: !0 }), I(d).forEach(E), p = R(Ge), w = P(Ge, v), S = R(Ge), A = b(Ge, "SPAN", { class: !0, "data-svelte-h": !0 }), Y(A) !== "svelte-y1n5j4" && (A.textContent = y), Ge.forEach(E), C = R(Be), D = b(Be, "BUTTON", { class: !0 });
      var qe = I(D);
      F = b(qe, "I", { class: !0 }), I(F).forEach(E), W = R(qe), se = P(qe, U), le = R(qe), X = b(qe, "SPAN", { class: !0, "data-svelte-h": !0 }), Y(X) !== "svelte-rmm9hi" && (X.textContent = ce), qe.forEach(E), ne = R(Be), Z = b(Be, "BUTTON", { class: !0, "data-svelte-h": !0 }), Y(Z) !== "svelte-1uo65l0" && (Z.innerHTML = pe), Be.forEach(E), x.forEach(E), this.h();
    },
    h() {
      zt(i.src, a = /*sentence*/
      r[0].audioUrl) || g(i, "src", a), g(i, "preload", "auto"), i.autoplay = !0, g(n, "class", "flashcard-content svelte-1ee5qgk"), g(d, "class", _ = "fas fa-" + /*state*/
      (r[2].stage === 1 ? "play" : "arrow-left")), g(A, "class", "shortcut-hint svelte-1ee5qgk"), g(h, "class", "flashcard-btn svelte-1ee5qgk"), h.disabled = O = /*buttonLabels*/
      r[5].leftDisabled, yt(
        h,
        "active",
        /*state*/
        r[2].stage === 1
      ), g(F, "class", V = "fas fa-" + /*state*/
      (r[2].stage < 3 ? "arrow-right" : "eye")), g(X, "class", "shortcut-hint svelte-1ee5qgk"), g(D, "class", "flashcard-btn svelte-1ee5qgk"), D.disabled = Q = /*buttonLabels*/
      r[5].rightDisabled, yt(
        D,
        "active",
        /*state*/
        r[2].stage === 3
      ), g(Z, "class", "flashcard-btn next-btn svelte-1ee5qgk"), g(u, "class", "flashcard-controls svelte-1ee5qgk"), g(e, "class", "flashcard svelte-1ee5qgk");
    },
    m(B, x) {
      L(B, e, x), j && j.m(e, null), f(e, t), z && z.m(e, null), f(e, s), f(e, n), f(n, i), r[12](i), f(n, l), ie && ie.m(n, null), f(n, o), te && te.m(n, null), f(e, c), f(e, u), f(u, h), f(h, d), f(h, p), f(h, w), f(h, S), f(h, A), f(u, C), f(u, D), f(D, F), f(D, W), f(D, se), f(D, le), f(D, X), f(u, ne), f(u, Z), H = !0, K || ($ = [
        re(
          h,
          "click",
          /*handleLeftClick*/
          r[6]
        ),
        re(
          D,
          "click",
          /*handleRightClick*/
          r[7]
        ),
        re(
          Z,
          "click",
          /*handleNextClick*/
          r[8]
        )
      ], K = !0);
    },
    p(B, [x]) {
      /*state*/
      B[2].error ? j ? j.p(B, x) : (j = Ls(B), j.c(), j.m(e, t)) : j && (j.d(1), j = null), /*state*/
      B[2].sourceFilter.type && /*state*/
      B[2].sourceFilter.slug ? z ? z.p(B, x) : (z = Ds(B), z.c(), z.m(e, s)) : z && (z.d(1), z = null), (!H || x & /*sentence*/
      1 && !zt(i.src, a = /*sentence*/
      B[0].audioUrl)) && g(i, "src", a), /*state*/
      B[2].stage >= 2 ? ie ? ie.p(B, x) : (ie = Us(B), ie.c(), ie.m(n, o)) : ie && (ie.d(1), ie = null), /*state*/
      B[2].stage >= 3 ? te ? (te.p(B, x), x & /*state*/
      4 && J(te, 1)) : (te = Vs(B), te.c(), J(te, 1), te.m(n, null)) : te && (Ue(), ae(te, 1, 1, () => {
        te = null;
      }), Ve()), (!H || x & /*state*/
      4 && _ !== (_ = "fas fa-" + /*state*/
      (B[2].stage === 1 ? "play" : "arrow-left"))) && g(d, "class", _), (!H || x & /*buttonLabels*/
      32) && v !== (v = /*buttonLabels*/
      B[5].left + "") && M(w, v), (!H || x & /*buttonLabels*/
      32 && O !== (O = /*buttonLabels*/
      B[5].leftDisabled)) && (h.disabled = O), (!H || x & /*state*/
      4) && yt(
        h,
        "active",
        /*state*/
        B[2].stage === 1
      ), (!H || x & /*state*/
      4 && V !== (V = "fas fa-" + /*state*/
      (B[2].stage < 3 ? "arrow-right" : "eye"))) && g(F, "class", V), (!H || x & /*buttonLabels*/
      32) && U !== (U = /*buttonLabels*/
      B[5].right + "") && M(se, U), (!H || x & /*buttonLabels*/
      32 && Q !== (Q = /*buttonLabels*/
      B[5].rightDisabled)) && (D.disabled = Q), (!H || x & /*state*/
      4) && yt(
        D,
        "active",
        /*state*/
        B[2].stage === 3
      );
    },
    i(B) {
      H || (J(te), H = !0);
    },
    o(B) {
      ae(te), H = !1;
    },
    d(B) {
      B && E(e), j && j.d(), z && z.d(), r[12](null), ie && ie.d(), te && te.d(), K = !1, ve($);
    }
  };
}
function Dn(r, e, t) {
  let s, { sentence: n } = e, { targetLanguageCode: i } = e;
  const a = "";
  let { sourcefile: l = null } = e, { sourcedir: o = null } = e, c = {
    stage: 1,
    sentence: n,
    isLoading: !1,
    error: null,
    sourceFilter: {
      type: l ? "sourcefile" : o ? "sourcedir" : null,
      slug: l || o || null
    }
  }, u, h = {};
  n.lemmaWords && n.lemmaWords.forEach((y) => {
    t(
      4,
      h[y] = {
        lemma: y,
        part_of_speech: "",
        translations: [],
        isLoading: !0,
        error: null
      },
      h
    );
  });
  async function d(y) {
    try {
      console.log(`Fetching lemma data for ${y} with language code ${i}`);
      const O = _e(de.LEMMA_API_GET_LEMMA_DATA_API, {
        target_language_code: i,
        lemma: y
      });
      console.log(`API URL: ${O}`);
      const C = await fetch(O);
      if (!C.ok)
        throw console.error(`API error status: ${C.status}`), new Error(`Failed to fetch lemma data for ${y}`);
      const D = await C.json();
      console.log("Lemma data received:", D), t(
        4,
        h[y] = {
          lemma: y,
          part_of_speech: D.part_of_speech || "",
          translations: D.translations || [],
          isLoading: !1,
          error: null
        },
        h
      );
    } catch (O) {
      console.error("Error fetching lemma data:", O), t(
        4,
        h[y] = {
          ...h[y],
          isLoading: !1,
          error: String(O)
        },
        h
      );
    }
  }
  function _() {
    c.stage === 1 ? w() : (t(2, c = kn(c)), c.stage === 1 && w());
  }
  function p() {
    s.rightDisabled || (t(2, c = Rn(c)), c.stage === 3 && n.lemmaWords && n.lemmaWords.length > 0 && n.lemmaWords.forEach(d));
  }
  function v() {
    const y = new URLSearchParams();
    l ? y.append("sourcefile", l) : o && y.append("sourcedir", o);
    const O = y.toString() ? `?${y.toString()}` : "", C = _e(de.FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW, { target_language_code: i });
    window.location.href = `${C}${O}`;
  }
  function w() {
    u && (t(3, u.currentTime = 0, u), u.play().catch((y) => {
      console.error("Error playing audio:", y), t(2, c = {
        ...c,
        error: "Audio couldn't autoplay. Please use the Play Audio button to listen."
      });
    }));
  }
  function S(y) {
    if (!(y.target instanceof HTMLInputElement || y.target instanceof HTMLTextAreaElement))
      switch (y.key) {
        case "ArrowLeft":
          _();
          break;
        case "ArrowRight":
          p();
          break;
        case "Enter":
          v();
          break;
      }
  }
  De(() => (document.addEventListener("keydown", S), () => {
    document.removeEventListener("keydown", S);
  }));
  function A(y) {
    tt[y ? "unshift" : "push"](() => {
      u = y, t(3, u);
    });
  }
  return r.$$set = (y) => {
    "sentence" in y && t(0, n = y.sentence), "targetLanguageCode" in y && t(1, i = y.targetLanguageCode), "sourcefile" in y && t(10, l = y.sourcefile), "sourcedir" in y && t(11, o = y.sourcedir);
  }, r.$$.update = () => {
    r.$$.dirty & /*state*/
    4 && t(5, s = Pn(c.stage));
  }, [
    n,
    i,
    c,
    u,
    h,
    s,
    _,
    p,
    v,
    a,
    l,
    o,
    A
  ];
}
class fr extends be {
  constructor(e) {
    super(), me(this, e, Dn, Ln, ge, {
      sentence: 0,
      targetLanguageCode: 1,
      targetLanguageName: 9,
      sourcefile: 10,
      sourcedir: 11
    });
  }
  get targetLanguageName() {
    return this.$$.ctx[9];
  }
}
function Fs(r) {
  let e, t, s, n = (
    /*sourcedir*/
    r[3] ? "directory" : "file"
  ), i, a, l, o = (
    /*sourcedir*/
    (r[3] || /*sourcefile*/
    r[2]) + ""
  ), c, u, h, d, _, p, v = (
    /*lemmaCount*/
    r[4] !== null && Ms(r)
  );
  return {
    c() {
      e = m("div"), t = m("i"), s = k(`
      Filtered by `), i = k(n), a = k(`: 
      `), l = m("strong"), c = k(o), u = T(), v && v.c(), h = T(), d = m("a"), _ = m("i"), this.h();
    },
    l(w) {
      e = b(w, "DIV", { class: !0 });
      var S = I(e);
      t = b(S, "I", { class: !0 }), I(t).forEach(E), s = P(S, `
      Filtered by `), i = P(S, n), a = P(S, `: 
      `), l = b(S, "STRONG", {});
      var A = I(l);
      c = P(A, o), A.forEach(E), u = R(S), v && v.l(S), h = R(S), d = b(S, "A", { href: !0, class: !0 });
      var y = I(d);
      _ = b(y, "I", { class: !0 }), I(_).forEach(E), y.forEach(E), S.forEach(E), this.h();
    },
    h() {
      g(t, "class", "ph-fill ph-filter svelte-hd0j5y"), g(_, "class", "ph-fill ph-x svelte-hd0j5y"), g(d, "href", p = _e(de.FLASHCARD_VIEWS_FLASHCARD_LANDING_VW, {
        target_language_code: (
          /*targetLanguageCode*/
          r[0]
        )
      })), g(d, "class", "clear-filter svelte-hd0j5y"), g(e, "class", "source-filter-banner svelte-hd0j5y");
    },
    m(w, S) {
      L(w, e, S), f(e, t), f(e, s), f(e, i), f(e, a), f(e, l), f(l, c), f(e, u), v && v.m(e, null), f(e, h), f(e, d), f(d, _);
    },
    p(w, S) {
      S & /*sourcedir*/
      8 && n !== (n = /*sourcedir*/
      w[3] ? "directory" : "file") && M(i, n), S & /*sourcedir, sourcefile*/
      12 && o !== (o = /*sourcedir*/
      (w[3] || /*sourcefile*/
      w[2]) + "") && M(c, o), /*lemmaCount*/
      w[4] !== null ? v ? v.p(w, S) : (v = Ms(w), v.c(), v.m(e, h)) : v && (v.d(1), v = null), S & /*targetLanguageCode*/
      1 && p !== (p = _e(de.FLASHCARD_VIEWS_FLASHCARD_LANDING_VW, {
        target_language_code: (
          /*targetLanguageCode*/
          w[0]
        )
      })) && g(d, "href", p);
    },
    d(w) {
      w && E(e), v && v.d();
    }
  };
}
function Ms(r) {
  let e, t, s, n;
  return {
    c() {
      e = m("span"), t = k("("), s = k(
        /*lemmaCount*/
        r[4]
      ), n = k(" words)"), this.h();
    },
    l(i) {
      e = b(i, "SPAN", { class: !0 });
      var a = I(e);
      t = P(a, "("), s = P(
        a,
        /*lemmaCount*/
        r[4]
      ), n = P(a, " words)"), a.forEach(E), this.h();
    },
    h() {
      g(e, "class", "lemma-count svelte-hd0j5y");
    },
    m(i, a) {
      L(i, e, a), f(e, t), f(e, s), f(e, n);
    },
    p(i, a) {
      a & /*lemmaCount*/
      16 && M(
        s,
        /*lemmaCount*/
        i[4]
      );
    },
    d(i) {
      i && E(e);
    }
  };
}
function Un(r) {
  let e, t, s, n, i, a, l, o, c, u, h = "Listen to the audio", d, _, p, v, w, S, A, y = "See the translation", O, C, D = `<strong>Keyboard shortcuts:</strong> <span class="shortcut svelte-hd0j5y">←</span> Previous stage
      <span class="shortcut svelte-hd0j5y">→</span> Next stage
      <span class="shortcut svelte-hd0j5y">Enter</span> New sentence`, F, V, W, U, se, le = "(Enter)", X, ce, Q = (
    /*sourcefile*/
    (r[2] || /*sourcedir*/
    r[3]) && Fs(r)
  );
  return {
    c() {
      e = m("div"), Q && Q.c(), t = T(), s = m("div"), n = m("p"), i = k("Practice your "), a = k(
        /*targetLanguageName*/
        r[1]
      ), l = k(` vocabulary with interactive flashcards.
      Each flashcard has three stages:`), o = T(), c = m("ol"), u = m("li"), u.textContent = h, d = T(), _ = m("li"), p = k("View the "), v = k(
        /*targetLanguageName*/
        r[1]
      ), w = k(" sentence"), S = T(), A = m("li"), A.textContent = y, O = T(), C = m("p"), C.innerHTML = D, F = T(), V = m("div"), W = m("a"), U = k("Start Flashcards "), se = m("span"), se.textContent = le, this.h();
    },
    l(ne) {
      e = b(ne, "DIV", { class: !0 });
      var Z = I(e);
      Q && Q.l(Z), t = R(Z), s = b(Z, "DIV", { class: !0 });
      var pe = I(s);
      n = b(pe, "P", {});
      var H = I(n);
      i = P(H, "Practice your "), a = P(
        H,
        /*targetLanguageName*/
        r[1]
      ), l = P(H, ` vocabulary with interactive flashcards.
      Each flashcard has three stages:`), H.forEach(E), o = R(pe), c = b(pe, "OL", {});
      var K = I(c);
      u = b(K, "LI", { "data-svelte-h": !0 }), Y(u) !== "svelte-1ngxlxl" && (u.textContent = h), d = R(K), _ = b(K, "LI", {});
      var $ = I(_);
      p = P($, "View the "), v = P(
        $,
        /*targetLanguageName*/
        r[1]
      ), w = P($, " sentence"), $.forEach(E), S = R(K), A = b(K, "LI", { "data-svelte-h": !0 }), Y(A) !== "svelte-uqycfj" && (A.textContent = y), K.forEach(E), O = R(pe), C = b(pe, "P", { class: !0, "data-svelte-h": !0 }), Y(C) !== "svelte-1qgj8dd" && (C.innerHTML = D), pe.forEach(E), F = R(Z), V = b(Z, "DIV", { class: !0 });
      var j = I(V);
      W = b(j, "A", { href: !0, class: !0 });
      var z = I(W);
      U = P(z, "Start Flashcards "), se = b(z, "SPAN", { class: !0, "data-svelte-h": !0 }), Y(se) !== "svelte-xq7gtu" && (se.textContent = le), z.forEach(E), j.forEach(E), Z.forEach(E), this.h();
    },
    h() {
      g(C, "class", "keyboard-hints svelte-hd0j5y"), g(s, "class", "flashcard-description svelte-hd0j5y"), g(se, "class", "shortcut-hint svelte-hd0j5y"), g(
        W,
        "href",
        /*startUrl*/
        r[5]
      ), g(W, "class", "start-button svelte-hd0j5y"), g(V, "class", "start-button-container svelte-hd0j5y"), g(e, "class", "flashcard-landing svelte-hd0j5y");
    },
    m(ne, Z) {
      L(ne, e, Z), Q && Q.m(e, null), f(e, t), f(e, s), f(s, n), f(n, i), f(n, a), f(n, l), f(s, o), f(s, c), f(c, u), f(c, d), f(c, _), f(_, p), f(_, v), f(_, w), f(c, S), f(c, A), f(s, O), f(s, C), f(e, F), f(e, V), f(V, W), f(W, U), f(W, se), X || (ce = re(
        W,
        "keydown",
        /*handleKeydown*/
        r[6]
      ), X = !0);
    },
    p(ne, [Z]) {
      /*sourcefile*/
      ne[2] || /*sourcedir*/
      ne[3] ? Q ? Q.p(ne, Z) : (Q = Fs(ne), Q.c(), Q.m(e, t)) : Q && (Q.d(1), Q = null), Z & /*targetLanguageName*/
      2 && M(
        a,
        /*targetLanguageName*/
        ne[1]
      ), Z & /*targetLanguageName*/
      2 && M(
        v,
        /*targetLanguageName*/
        ne[1]
      ), Z & /*startUrl*/
      32 && g(
        W,
        "href",
        /*startUrl*/
        ne[5]
      );
    },
    i: q,
    o: q,
    d(ne) {
      ne && E(e), Q && Q.d(), X = !1, ce();
    }
  };
}
function Vn(r, e, t) {
  let { targetLanguageCode: s } = e, { targetLanguageName: n } = e, { sourcefile: i = null } = e, { sourcedir: a = null } = e, { lemmaCount: l = null } = e, c = _e(de.FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW, { target_language_code: s });
  i ? c += `?sourcefile=${i}` : a && (c += `?sourcedir=${a}`);
  function u(h) {
    h.key === "Enter" && (window.location.href = c);
  }
  return r.$$set = (h) => {
    "targetLanguageCode" in h && t(0, s = h.targetLanguageCode), "targetLanguageName" in h && t(1, n = h.targetLanguageName), "sourcefile" in h && t(2, i = h.sourcefile), "sourcedir" in h && t(3, a = h.sourcedir), "lemmaCount" in h && t(4, l = h.lemmaCount);
  }, [
    s,
    n,
    i,
    a,
    l,
    c,
    u
  ];
}
class _r extends be {
  constructor(e) {
    super(), me(this, e, Vn, Un, ge, {
      targetLanguageCode: 0,
      targetLanguageName: 1,
      sourcefile: 2,
      sourcedir: 3,
      lemmaCount: 4
    });
  }
}
const xe = [];
function Wn(r, e) {
  return {
    subscribe: gr(r, e).subscribe
  };
}
function gr(r, e = q) {
  let t;
  const s = /* @__PURE__ */ new Set();
  function n(l) {
    if (ge(r, l) && (r = l, t)) {
      const o = !xe.length;
      for (const c of s)
        c[1](), xe.push(c, r);
      if (o) {
        for (let c = 0; c < xe.length; c += 2)
          xe[c][0](xe[c + 1]);
        xe.length = 0;
      }
    }
  }
  function i(l) {
    n(l(r));
  }
  function a(l, o = q) {
    const c = [l, o];
    return s.add(c), s.size === 1 && (t = e(n, i) || q), l(r), () => {
      s.delete(c), s.size === 0 && t && (t(), t = null);
    };
  }
  return { set: n, update: i, subscribe: a };
}
function Pt(r, e, t) {
  const s = !Array.isArray(r), n = s ? [r] : r;
  if (!n.every(Boolean))
    throw new Error("derived() expects stores as input, got a falsy value");
  const i = e.length < 2;
  return Wn(t, (a, l) => {
    let o = !1;
    const c = [];
    let u = 0, h = q;
    const d = () => {
      if (u)
        return;
      h();
      const p = e(s ? c[0] : c, a, l);
      i ? a(p) : h = rs(p) ? p : q;
    }, _ = n.map(
      (p, v) => nr(
        p,
        (w) => {
          c[v] = w, u &= ~(1 << v), o && d();
        },
        () => {
          u |= 1 << v;
        }
      )
    );
    return o = !0, d(), function() {
      ve(_), h(), o = !1;
    };
  });
}
const jn = (r) => {
  let e;
  return r ? e = r : typeof fetch > "u" ? e = (...t) => Promise.resolve().then(() => at).then(({ default: s }) => s(...t)) : e = fetch, (...t) => e(...t);
};
class as extends Error {
  constructor(e, t = "FunctionsError", s) {
    super(e), this.name = t, this.context = s;
  }
}
class Nn extends as {
  constructor(e) {
    super("Failed to send a request to the Edge Function", "FunctionsFetchError", e);
  }
}
class Fn extends as {
  constructor(e) {
    super("Relay Error invoking the Edge Function", "FunctionsRelayError", e);
  }
}
class Mn extends as {
  constructor(e) {
    super("Edge Function returned a non-2xx status code", "FunctionsHttpError", e);
  }
}
var Kt;
(function(r) {
  r.Any = "any", r.ApNortheast1 = "ap-northeast-1", r.ApNortheast2 = "ap-northeast-2", r.ApSouth1 = "ap-south-1", r.ApSoutheast1 = "ap-southeast-1", r.ApSoutheast2 = "ap-southeast-2", r.CaCentral1 = "ca-central-1", r.EuCentral1 = "eu-central-1", r.EuWest1 = "eu-west-1", r.EuWest2 = "eu-west-2", r.EuWest3 = "eu-west-3", r.SaEast1 = "sa-east-1", r.UsEast1 = "us-east-1", r.UsWest1 = "us-west-1", r.UsWest2 = "us-west-2";
})(Kt || (Kt = {}));
var Hn = function(r, e, t, s) {
  function n(i) {
    return i instanceof t ? i : new t(function(a) {
      a(i);
    });
  }
  return new (t || (t = Promise))(function(i, a) {
    function l(u) {
      try {
        c(s.next(u));
      } catch (h) {
        a(h);
      }
    }
    function o(u) {
      try {
        c(s.throw(u));
      } catch (h) {
        a(h);
      }
    }
    function c(u) {
      u.done ? i(u.value) : n(u.value).then(l, o);
    }
    c((s = s.apply(r, e || [])).next());
  });
};
class $n {
  constructor(e, { headers: t = {}, customFetch: s, region: n = Kt.Any } = {}) {
    this.url = e, this.headers = t, this.region = n, this.fetch = jn(s);
  }
  /**
   * Updates the authorization header
   * @param token - the new jwt token sent in the authorisation header
   */
  setAuth(e) {
    this.headers.Authorization = `Bearer ${e}`;
  }
  /**
   * Invokes a function
   * @param functionName - The name of the Function to invoke.
   * @param options - Options for invoking the Function.
   */
  invoke(e, t = {}) {
    var s;
    return Hn(this, void 0, void 0, function* () {
      try {
        const { headers: n, method: i, body: a } = t;
        let l = {}, { region: o } = t;
        o || (o = this.region), o && o !== "any" && (l["x-region"] = o);
        let c;
        a && (n && !Object.prototype.hasOwnProperty.call(n, "Content-Type") || !n) && (typeof Blob < "u" && a instanceof Blob || a instanceof ArrayBuffer ? (l["Content-Type"] = "application/octet-stream", c = a) : typeof a == "string" ? (l["Content-Type"] = "text/plain", c = a) : typeof FormData < "u" && a instanceof FormData ? c = a : (l["Content-Type"] = "application/json", c = JSON.stringify(a)));
        const u = yield this.fetch(`${this.url}/${e}`, {
          method: i || "POST",
          // headers priority is (high to low):
          // 1. invoke-level headers
          // 2. client-level headers
          // 3. default Content-Type header
          headers: Object.assign(Object.assign(Object.assign({}, l), this.headers), n),
          body: c
        }).catch((p) => {
          throw new Nn(p);
        }), h = u.headers.get("x-relay-error");
        if (h && h === "true")
          throw new Fn(u);
        if (!u.ok)
          throw new Mn(u);
        let d = ((s = u.headers.get("Content-Type")) !== null && s !== void 0 ? s : "text/plain").split(";")[0].trim(), _;
        return d === "application/json" ? _ = yield u.json() : d === "application/octet-stream" ? _ = yield u.blob() : d === "text/event-stream" ? _ = u : d === "multipart/form-data" ? _ = yield u.formData() : _ = yield u.text(), { data: _, error: null };
      } catch (n) {
        return { data: null, error: n };
      }
    });
  }
}
var Ee = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {};
function ho(r) {
  return r && r.__esModule && Object.prototype.hasOwnProperty.call(r, "default") ? r.default : r;
}
function Bn(r) {
  if (r.__esModule) return r;
  var e = r.default;
  if (typeof e == "function") {
    var t = function s() {
      return this instanceof s ? Reflect.construct(e, arguments, this.constructor) : e.apply(this, arguments);
    };
    t.prototype = e.prototype;
  } else t = {};
  return Object.defineProperty(t, "__esModule", { value: !0 }), Object.keys(r).forEach(function(s) {
    var n = Object.getOwnPropertyDescriptor(r, s);
    Object.defineProperty(t, s, n.get ? n : {
      enumerable: !0,
      get: function() {
        return r[s];
      }
    });
  }), t;
}
var he = {}, os = {}, Lt = {}, vt = {}, Dt = {}, Ut = {}, Gn = function() {
  if (typeof self < "u")
    return self;
  if (typeof window < "u")
    return window;
  if (typeof global < "u")
    return global;
  throw new Error("unable to locate global object");
}, rt = Gn();
const qn = rt.fetch, pr = rt.fetch.bind(rt), Er = rt.Headers, zn = rt.Request, xn = rt.Response, at = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  Headers: Er,
  Request: zn,
  Response: xn,
  default: pr,
  fetch: qn
}, Symbol.toStringTag, { value: "Module" })), Jn = /* @__PURE__ */ Bn(at);
var Vt = {};
Object.defineProperty(Vt, "__esModule", { value: !0 });
let Kn = class extends Error {
  constructor(e) {
    super(e.message), this.name = "PostgrestError", this.details = e.details, this.hint = e.hint, this.code = e.code;
  }
};
Vt.default = Kn;
var vr = Ee && Ee.__importDefault || function(r) {
  return r && r.__esModule ? r : { default: r };
};
Object.defineProperty(Ut, "__esModule", { value: !0 });
const Yn = vr(Jn), Xn = vr(Vt);
let Qn = class {
  constructor(e) {
    this.shouldThrowOnError = !1, this.method = e.method, this.url = e.url, this.headers = e.headers, this.schema = e.schema, this.body = e.body, this.shouldThrowOnError = e.shouldThrowOnError, this.signal = e.signal, this.isMaybeSingle = e.isMaybeSingle, e.fetch ? this.fetch = e.fetch : typeof fetch > "u" ? this.fetch = Yn.default : this.fetch = fetch;
  }
  /**
   * If there's an error with the query, throwOnError will reject the promise by
   * throwing the error instead of returning it as part of a successful response.
   *
   * {@link https://github.com/supabase/supabase-js/issues/92}
   */
  throwOnError() {
    return this.shouldThrowOnError = !0, this;
  }
  /**
   * Set an HTTP header for the request.
   */
  setHeader(e, t) {
    return this.headers = Object.assign({}, this.headers), this.headers[e] = t, this;
  }
  then(e, t) {
    this.schema === void 0 || (["GET", "HEAD"].includes(this.method) ? this.headers["Accept-Profile"] = this.schema : this.headers["Content-Profile"] = this.schema), this.method !== "GET" && this.method !== "HEAD" && (this.headers["Content-Type"] = "application/json");
    const s = this.fetch;
    let n = s(this.url.toString(), {
      method: this.method,
      headers: this.headers,
      body: JSON.stringify(this.body),
      signal: this.signal
    }).then(async (i) => {
      var a, l, o;
      let c = null, u = null, h = null, d = i.status, _ = i.statusText;
      if (i.ok) {
        if (this.method !== "HEAD") {
          const S = await i.text();
          S === "" || (this.headers.Accept === "text/csv" || this.headers.Accept && this.headers.Accept.includes("application/vnd.pgrst.plan+text") ? u = S : u = JSON.parse(S));
        }
        const v = (a = this.headers.Prefer) === null || a === void 0 ? void 0 : a.match(/count=(exact|planned|estimated)/), w = (l = i.headers.get("content-range")) === null || l === void 0 ? void 0 : l.split("/");
        v && w && w.length > 1 && (h = parseInt(w[1])), this.isMaybeSingle && this.method === "GET" && Array.isArray(u) && (u.length > 1 ? (c = {
          // https://github.com/PostgREST/postgrest/blob/a867d79c42419af16c18c3fb019eba8df992626f/src/PostgREST/Error.hs#L553
          code: "PGRST116",
          details: `Results contain ${u.length} rows, application/vnd.pgrst.object+json requires 1 row`,
          hint: null,
          message: "JSON object requested, multiple (or no) rows returned"
        }, u = null, h = null, d = 406, _ = "Not Acceptable") : u.length === 1 ? u = u[0] : u = null);
      } else {
        const v = await i.text();
        try {
          c = JSON.parse(v), Array.isArray(c) && i.status === 404 && (u = [], c = null, d = 200, _ = "OK");
        } catch {
          i.status === 404 && v === "" ? (d = 204, _ = "No Content") : c = {
            message: v
          };
        }
        if (c && this.isMaybeSingle && (!((o = c == null ? void 0 : c.details) === null || o === void 0) && o.includes("0 rows")) && (c = null, d = 200, _ = "OK"), c && this.shouldThrowOnError)
          throw new Xn.default(c);
      }
      return {
        error: c,
        data: u,
        count: h,
        status: d,
        statusText: _
      };
    });
    return this.shouldThrowOnError || (n = n.catch((i) => {
      var a, l, o;
      return {
        error: {
          message: `${(a = i == null ? void 0 : i.name) !== null && a !== void 0 ? a : "FetchError"}: ${i == null ? void 0 : i.message}`,
          details: `${(l = i == null ? void 0 : i.stack) !== null && l !== void 0 ? l : ""}`,
          hint: "",
          code: `${(o = i == null ? void 0 : i.code) !== null && o !== void 0 ? o : ""}`
        },
        data: null,
        count: null,
        status: 0,
        statusText: ""
      };
    })), n.then(e, t);
  }
  /**
   * Override the type of the returned `data`.
   *
   * @typeParam NewResult - The new result type to override with
   * @deprecated Use overrideTypes<yourType, { merge: false }>() method at the end of your call chain instead
   */
  returns() {
    return this;
  }
  /**
   * Override the type of the returned `data` field in the response.
   *
   * @typeParam NewResult - The new type to cast the response data to
   * @typeParam Options - Optional type configuration (defaults to { merge: true })
   * @typeParam Options.merge - When true, merges the new type with existing return type. When false, replaces the existing types entirely (defaults to true)
   * @example
   * ```typescript
   * // Merge with existing types (default behavior)
   * const query = supabase
   *   .from('users')
   *   .select()
   *   .overrideTypes<{ custom_field: string }>()
   *
   * // Replace existing types completely
   * const replaceQuery = supabase
   *   .from('users')
   *   .select()
   *   .overrideTypes<{ id: number; name: string }, { merge: false }>()
   * ```
   * @returns A PostgrestBuilder instance with the new type
   */
  overrideTypes() {
    return this;
  }
};
Ut.default = Qn;
var Zn = Ee && Ee.__importDefault || function(r) {
  return r && r.__esModule ? r : { default: r };
};
Object.defineProperty(Dt, "__esModule", { value: !0 });
const ei = Zn(Ut);
let ti = class extends ei.default {
  /**
   * Perform a SELECT on the query result.
   *
   * By default, `.insert()`, `.update()`, `.upsert()`, and `.delete()` do not
   * return modified rows. By calling this method, modified rows are returned in
   * `data`.
   *
   * @param columns - The columns to retrieve, separated by commas
   */
  select(e) {
    let t = !1;
    const s = (e ?? "*").split("").map((n) => /\s/.test(n) && !t ? "" : (n === '"' && (t = !t), n)).join("");
    return this.url.searchParams.set("select", s), this.headers.Prefer && (this.headers.Prefer += ","), this.headers.Prefer += "return=representation", this;
  }
  /**
   * Order the query result by `column`.
   *
   * You can call this method multiple times to order by multiple columns.
   *
   * You can order referenced tables, but it only affects the ordering of the
   * parent table if you use `!inner` in the query.
   *
   * @param column - The column to order by
   * @param options - Named parameters
   * @param options.ascending - If `true`, the result will be in ascending order
   * @param options.nullsFirst - If `true`, `null`s appear first. If `false`,
   * `null`s appear last.
   * @param options.referencedTable - Set this to order a referenced table by
   * its columns
   * @param options.foreignTable - Deprecated, use `options.referencedTable`
   * instead
   */
  order(e, { ascending: t = !0, nullsFirst: s, foreignTable: n, referencedTable: i = n } = {}) {
    const a = i ? `${i}.order` : "order", l = this.url.searchParams.get(a);
    return this.url.searchParams.set(a, `${l ? `${l},` : ""}${e}.${t ? "asc" : "desc"}${s === void 0 ? "" : s ? ".nullsfirst" : ".nullslast"}`), this;
  }
  /**
   * Limit the query result by `count`.
   *
   * @param count - The maximum number of rows to return
   * @param options - Named parameters
   * @param options.referencedTable - Set this to limit rows of referenced
   * tables instead of the parent table
   * @param options.foreignTable - Deprecated, use `options.referencedTable`
   * instead
   */
  limit(e, { foreignTable: t, referencedTable: s = t } = {}) {
    const n = typeof s > "u" ? "limit" : `${s}.limit`;
    return this.url.searchParams.set(n, `${e}`), this;
  }
  /**
   * Limit the query result by starting at an offset `from` and ending at the offset `to`.
   * Only records within this range are returned.
   * This respects the query order and if there is no order clause the range could behave unexpectedly.
   * The `from` and `to` values are 0-based and inclusive: `range(1, 3)` will include the second, third
   * and fourth rows of the query.
   *
   * @param from - The starting index from which to limit the result
   * @param to - The last index to which to limit the result
   * @param options - Named parameters
   * @param options.referencedTable - Set this to limit rows of referenced
   * tables instead of the parent table
   * @param options.foreignTable - Deprecated, use `options.referencedTable`
   * instead
   */
  range(e, t, { foreignTable: s, referencedTable: n = s } = {}) {
    const i = typeof n > "u" ? "offset" : `${n}.offset`, a = typeof n > "u" ? "limit" : `${n}.limit`;
    return this.url.searchParams.set(i, `${e}`), this.url.searchParams.set(a, `${t - e + 1}`), this;
  }
  /**
   * Set the AbortSignal for the fetch request.
   *
   * @param signal - The AbortSignal to use for the fetch request
   */
  abortSignal(e) {
    return this.signal = e, this;
  }
  /**
   * Return `data` as a single object instead of an array of objects.
   *
   * Query result must be one row (e.g. using `.limit(1)`), otherwise this
   * returns an error.
   */
  single() {
    return this.headers.Accept = "application/vnd.pgrst.object+json", this;
  }
  /**
   * Return `data` as a single object instead of an array of objects.
   *
   * Query result must be zero or one row (e.g. using `.limit(1)`), otherwise
   * this returns an error.
   */
  maybeSingle() {
    return this.method === "GET" ? this.headers.Accept = "application/json" : this.headers.Accept = "application/vnd.pgrst.object+json", this.isMaybeSingle = !0, this;
  }
  /**
   * Return `data` as a string in CSV format.
   */
  csv() {
    return this.headers.Accept = "text/csv", this;
  }
  /**
   * Return `data` as an object in [GeoJSON](https://geojson.org) format.
   */
  geojson() {
    return this.headers.Accept = "application/geo+json", this;
  }
  /**
   * Return `data` as the EXPLAIN plan for the query.
   *
   * You need to enable the
   * [db_plan_enabled](https://supabase.com/docs/guides/database/debugging-performance#enabling-explain)
   * setting before using this method.
   *
   * @param options - Named parameters
   *
   * @param options.analyze - If `true`, the query will be executed and the
   * actual run time will be returned
   *
   * @param options.verbose - If `true`, the query identifier will be returned
   * and `data` will include the output columns of the query
   *
   * @param options.settings - If `true`, include information on configuration
   * parameters that affect query planning
   *
   * @param options.buffers - If `true`, include information on buffer usage
   *
   * @param options.wal - If `true`, include information on WAL record generation
   *
   * @param options.format - The format of the output, can be `"text"` (default)
   * or `"json"`
   */
  explain({ analyze: e = !1, verbose: t = !1, settings: s = !1, buffers: n = !1, wal: i = !1, format: a = "text" } = {}) {
    var l;
    const o = [
      e ? "analyze" : null,
      t ? "verbose" : null,
      s ? "settings" : null,
      n ? "buffers" : null,
      i ? "wal" : null
    ].filter(Boolean).join("|"), c = (l = this.headers.Accept) !== null && l !== void 0 ? l : "application/json";
    return this.headers.Accept = `application/vnd.pgrst.plan+${a}; for="${c}"; options=${o};`, a === "json" ? this : this;
  }
  /**
   * Rollback the query.
   *
   * `data` will still be returned, but the query is not committed.
   */
  rollback() {
    var e;
    return ((e = this.headers.Prefer) !== null && e !== void 0 ? e : "").trim().length > 0 ? this.headers.Prefer += ",tx=rollback" : this.headers.Prefer = "tx=rollback", this;
  }
  /**
   * Override the type of the returned `data`.
   *
   * @typeParam NewResult - The new result type to override with
   * @deprecated Use overrideTypes<yourType, { merge: false }>() method at the end of your call chain instead
   */
  returns() {
    return this;
  }
};
Dt.default = ti;
var si = Ee && Ee.__importDefault || function(r) {
  return r && r.__esModule ? r : { default: r };
};
Object.defineProperty(vt, "__esModule", { value: !0 });
const ri = si(Dt);
let ni = class extends ri.default {
  /**
   * Match only rows where `column` is equal to `value`.
   *
   * To check if the value of `column` is NULL, you should use `.is()` instead.
   *
   * @param column - The column to filter on
   * @param value - The value to filter with
   */
  eq(e, t) {
    return this.url.searchParams.append(e, `eq.${t}`), this;
  }
  /**
   * Match only rows where `column` is not equal to `value`.
   *
   * @param column - The column to filter on
   * @param value - The value to filter with
   */
  neq(e, t) {
    return this.url.searchParams.append(e, `neq.${t}`), this;
  }
  /**
   * Match only rows where `column` is greater than `value`.
   *
   * @param column - The column to filter on
   * @param value - The value to filter with
   */
  gt(e, t) {
    return this.url.searchParams.append(e, `gt.${t}`), this;
  }
  /**
   * Match only rows where `column` is greater than or equal to `value`.
   *
   * @param column - The column to filter on
   * @param value - The value to filter with
   */
  gte(e, t) {
    return this.url.searchParams.append(e, `gte.${t}`), this;
  }
  /**
   * Match only rows where `column` is less than `value`.
   *
   * @param column - The column to filter on
   * @param value - The value to filter with
   */
  lt(e, t) {
    return this.url.searchParams.append(e, `lt.${t}`), this;
  }
  /**
   * Match only rows where `column` is less than or equal to `value`.
   *
   * @param column - The column to filter on
   * @param value - The value to filter with
   */
  lte(e, t) {
    return this.url.searchParams.append(e, `lte.${t}`), this;
  }
  /**
   * Match only rows where `column` matches `pattern` case-sensitively.
   *
   * @param column - The column to filter on
   * @param pattern - The pattern to match with
   */
  like(e, t) {
    return this.url.searchParams.append(e, `like.${t}`), this;
  }
  /**
   * Match only rows where `column` matches all of `patterns` case-sensitively.
   *
   * @param column - The column to filter on
   * @param patterns - The patterns to match with
   */
  likeAllOf(e, t) {
    return this.url.searchParams.append(e, `like(all).{${t.join(",")}}`), this;
  }
  /**
   * Match only rows where `column` matches any of `patterns` case-sensitively.
   *
   * @param column - The column to filter on
   * @param patterns - The patterns to match with
   */
  likeAnyOf(e, t) {
    return this.url.searchParams.append(e, `like(any).{${t.join(",")}}`), this;
  }
  /**
   * Match only rows where `column` matches `pattern` case-insensitively.
   *
   * @param column - The column to filter on
   * @param pattern - The pattern to match with
   */
  ilike(e, t) {
    return this.url.searchParams.append(e, `ilike.${t}`), this;
  }
  /**
   * Match only rows where `column` matches all of `patterns` case-insensitively.
   *
   * @param column - The column to filter on
   * @param patterns - The patterns to match with
   */
  ilikeAllOf(e, t) {
    return this.url.searchParams.append(e, `ilike(all).{${t.join(",")}}`), this;
  }
  /**
   * Match only rows where `column` matches any of `patterns` case-insensitively.
   *
   * @param column - The column to filter on
   * @param patterns - The patterns to match with
   */
  ilikeAnyOf(e, t) {
    return this.url.searchParams.append(e, `ilike(any).{${t.join(",")}}`), this;
  }
  /**
   * Match only rows where `column` IS `value`.
   *
   * For non-boolean columns, this is only relevant for checking if the value of
   * `column` is NULL by setting `value` to `null`.
   *
   * For boolean columns, you can also set `value` to `true` or `false` and it
   * will behave the same way as `.eq()`.
   *
   * @param column - The column to filter on
   * @param value - The value to filter with
   */
  is(e, t) {
    return this.url.searchParams.append(e, `is.${t}`), this;
  }
  /**
   * Match only rows where `column` is included in the `values` array.
   *
   * @param column - The column to filter on
   * @param values - The values array to filter with
   */
  in(e, t) {
    const s = Array.from(new Set(t)).map((n) => typeof n == "string" && new RegExp("[,()]").test(n) ? `"${n}"` : `${n}`).join(",");
    return this.url.searchParams.append(e, `in.(${s})`), this;
  }
  /**
   * Only relevant for jsonb, array, and range columns. Match only rows where
   * `column` contains every element appearing in `value`.
   *
   * @param column - The jsonb, array, or range column to filter on
   * @param value - The jsonb, array, or range value to filter with
   */
  contains(e, t) {
    return typeof t == "string" ? this.url.searchParams.append(e, `cs.${t}`) : Array.isArray(t) ? this.url.searchParams.append(e, `cs.{${t.join(",")}}`) : this.url.searchParams.append(e, `cs.${JSON.stringify(t)}`), this;
  }
  /**
   * Only relevant for jsonb, array, and range columns. Match only rows where
   * every element appearing in `column` is contained by `value`.
   *
   * @param column - The jsonb, array, or range column to filter on
   * @param value - The jsonb, array, or range value to filter with
   */
  containedBy(e, t) {
    return typeof t == "string" ? this.url.searchParams.append(e, `cd.${t}`) : Array.isArray(t) ? this.url.searchParams.append(e, `cd.{${t.join(",")}}`) : this.url.searchParams.append(e, `cd.${JSON.stringify(t)}`), this;
  }
  /**
   * Only relevant for range columns. Match only rows where every element in
   * `column` is greater than any element in `range`.
   *
   * @param column - The range column to filter on
   * @param range - The range to filter with
   */
  rangeGt(e, t) {
    return this.url.searchParams.append(e, `sr.${t}`), this;
  }
  /**
   * Only relevant for range columns. Match only rows where every element in
   * `column` is either contained in `range` or greater than any element in
   * `range`.
   *
   * @param column - The range column to filter on
   * @param range - The range to filter with
   */
  rangeGte(e, t) {
    return this.url.searchParams.append(e, `nxl.${t}`), this;
  }
  /**
   * Only relevant for range columns. Match only rows where every element in
   * `column` is less than any element in `range`.
   *
   * @param column - The range column to filter on
   * @param range - The range to filter with
   */
  rangeLt(e, t) {
    return this.url.searchParams.append(e, `sl.${t}`), this;
  }
  /**
   * Only relevant for range columns. Match only rows where every element in
   * `column` is either contained in `range` or less than any element in
   * `range`.
   *
   * @param column - The range column to filter on
   * @param range - The range to filter with
   */
  rangeLte(e, t) {
    return this.url.searchParams.append(e, `nxr.${t}`), this;
  }
  /**
   * Only relevant for range columns. Match only rows where `column` is
   * mutually exclusive to `range` and there can be no element between the two
   * ranges.
   *
   * @param column - The range column to filter on
   * @param range - The range to filter with
   */
  rangeAdjacent(e, t) {
    return this.url.searchParams.append(e, `adj.${t}`), this;
  }
  /**
   * Only relevant for array and range columns. Match only rows where
   * `column` and `value` have an element in common.
   *
   * @param column - The array or range column to filter on
   * @param value - The array or range value to filter with
   */
  overlaps(e, t) {
    return typeof t == "string" ? this.url.searchParams.append(e, `ov.${t}`) : this.url.searchParams.append(e, `ov.{${t.join(",")}}`), this;
  }
  /**
   * Only relevant for text and tsvector columns. Match only rows where
   * `column` matches the query string in `query`.
   *
   * @param column - The text or tsvector column to filter on
   * @param query - The query text to match with
   * @param options - Named parameters
   * @param options.config - The text search configuration to use
   * @param options.type - Change how the `query` text is interpreted
   */
  textSearch(e, t, { config: s, type: n } = {}) {
    let i = "";
    n === "plain" ? i = "pl" : n === "phrase" ? i = "ph" : n === "websearch" && (i = "w");
    const a = s === void 0 ? "" : `(${s})`;
    return this.url.searchParams.append(e, `${i}fts${a}.${t}`), this;
  }
  /**
   * Match only rows where each column in `query` keys is equal to its
   * associated value. Shorthand for multiple `.eq()`s.
   *
   * @param query - The object to filter with, with column names as keys mapped
   * to their filter values
   */
  match(e) {
    return Object.entries(e).forEach(([t, s]) => {
      this.url.searchParams.append(t, `eq.${s}`);
    }), this;
  }
  /**
   * Match only rows which doesn't satisfy the filter.
   *
   * Unlike most filters, `opearator` and `value` are used as-is and need to
   * follow [PostgREST
   * syntax](https://postgrest.org/en/stable/api.html#operators). You also need
   * to make sure they are properly sanitized.
   *
   * @param column - The column to filter on
   * @param operator - The operator to be negated to filter with, following
   * PostgREST syntax
   * @param value - The value to filter with, following PostgREST syntax
   */
  not(e, t, s) {
    return this.url.searchParams.append(e, `not.${t}.${s}`), this;
  }
  /**
   * Match only rows which satisfy at least one of the filters.
   *
   * Unlike most filters, `filters` is used as-is and needs to follow [PostgREST
   * syntax](https://postgrest.org/en/stable/api.html#operators). You also need
   * to make sure it's properly sanitized.
   *
   * It's currently not possible to do an `.or()` filter across multiple tables.
   *
   * @param filters - The filters to use, following PostgREST syntax
   * @param options - Named parameters
   * @param options.referencedTable - Set this to filter on referenced tables
   * instead of the parent table
   * @param options.foreignTable - Deprecated, use `referencedTable` instead
   */
  or(e, { foreignTable: t, referencedTable: s = t } = {}) {
    const n = s ? `${s}.or` : "or";
    return this.url.searchParams.append(n, `(${e})`), this;
  }
  /**
   * Match only rows which satisfy the filter. This is an escape hatch - you
   * should use the specific filter methods wherever possible.
   *
   * Unlike most filters, `opearator` and `value` are used as-is and need to
   * follow [PostgREST
   * syntax](https://postgrest.org/en/stable/api.html#operators). You also need
   * to make sure they are properly sanitized.
   *
   * @param column - The column to filter on
   * @param operator - The operator to filter with, following PostgREST syntax
   * @param value - The value to filter with, following PostgREST syntax
   */
  filter(e, t, s) {
    return this.url.searchParams.append(e, `${t}.${s}`), this;
  }
};
vt.default = ni;
var ii = Ee && Ee.__importDefault || function(r) {
  return r && r.__esModule ? r : { default: r };
};
Object.defineProperty(Lt, "__esModule", { value: !0 });
const lt = ii(vt);
let ai = class {
  constructor(e, { headers: t = {}, schema: s, fetch: n }) {
    this.url = e, this.headers = t, this.schema = s, this.fetch = n;
  }
  /**
   * Perform a SELECT query on the table or view.
   *
   * @param columns - The columns to retrieve, separated by commas. Columns can be renamed when returned with `customName:columnName`
   *
   * @param options - Named parameters
   *
   * @param options.head - When set to `true`, `data` will not be returned.
   * Useful if you only need the count.
   *
   * @param options.count - Count algorithm to use to count rows in the table or view.
   *
   * `"exact"`: Exact but slow count algorithm. Performs a `COUNT(*)` under the
   * hood.
   *
   * `"planned"`: Approximated but fast count algorithm. Uses the Postgres
   * statistics under the hood.
   *
   * `"estimated"`: Uses exact count for low numbers and planned count for high
   * numbers.
   */
  select(e, { head: t = !1, count: s } = {}) {
    const n = t ? "HEAD" : "GET";
    let i = !1;
    const a = (e ?? "*").split("").map((l) => /\s/.test(l) && !i ? "" : (l === '"' && (i = !i), l)).join("");
    return this.url.searchParams.set("select", a), s && (this.headers.Prefer = `count=${s}`), new lt.default({
      method: n,
      url: this.url,
      headers: this.headers,
      schema: this.schema,
      fetch: this.fetch,
      allowEmpty: !1
    });
  }
  /**
   * Perform an INSERT into the table or view.
   *
   * By default, inserted rows are not returned. To return it, chain the call
   * with `.select()`.
   *
   * @param values - The values to insert. Pass an object to insert a single row
   * or an array to insert multiple rows.
   *
   * @param options - Named parameters
   *
   * @param options.count - Count algorithm to use to count inserted rows.
   *
   * `"exact"`: Exact but slow count algorithm. Performs a `COUNT(*)` under the
   * hood.
   *
   * `"planned"`: Approximated but fast count algorithm. Uses the Postgres
   * statistics under the hood.
   *
   * `"estimated"`: Uses exact count for low numbers and planned count for high
   * numbers.
   *
   * @param options.defaultToNull - Make missing fields default to `null`.
   * Otherwise, use the default value for the column. Only applies for bulk
   * inserts.
   */
  insert(e, { count: t, defaultToNull: s = !0 } = {}) {
    const n = "POST", i = [];
    if (this.headers.Prefer && i.push(this.headers.Prefer), t && i.push(`count=${t}`), s || i.push("missing=default"), this.headers.Prefer = i.join(","), Array.isArray(e)) {
      const a = e.reduce((l, o) => l.concat(Object.keys(o)), []);
      if (a.length > 0) {
        const l = [...new Set(a)].map((o) => `"${o}"`);
        this.url.searchParams.set("columns", l.join(","));
      }
    }
    return new lt.default({
      method: n,
      url: this.url,
      headers: this.headers,
      schema: this.schema,
      body: e,
      fetch: this.fetch,
      allowEmpty: !1
    });
  }
  /**
   * Perform an UPSERT on the table or view. Depending on the column(s) passed
   * to `onConflict`, `.upsert()` allows you to perform the equivalent of
   * `.insert()` if a row with the corresponding `onConflict` columns doesn't
   * exist, or if it does exist, perform an alternative action depending on
   * `ignoreDuplicates`.
   *
   * By default, upserted rows are not returned. To return it, chain the call
   * with `.select()`.
   *
   * @param values - The values to upsert with. Pass an object to upsert a
   * single row or an array to upsert multiple rows.
   *
   * @param options - Named parameters
   *
   * @param options.onConflict - Comma-separated UNIQUE column(s) to specify how
   * duplicate rows are determined. Two rows are duplicates if all the
   * `onConflict` columns are equal.
   *
   * @param options.ignoreDuplicates - If `true`, duplicate rows are ignored. If
   * `false`, duplicate rows are merged with existing rows.
   *
   * @param options.count - Count algorithm to use to count upserted rows.
   *
   * `"exact"`: Exact but slow count algorithm. Performs a `COUNT(*)` under the
   * hood.
   *
   * `"planned"`: Approximated but fast count algorithm. Uses the Postgres
   * statistics under the hood.
   *
   * `"estimated"`: Uses exact count for low numbers and planned count for high
   * numbers.
   *
   * @param options.defaultToNull - Make missing fields default to `null`.
   * Otherwise, use the default value for the column. This only applies when
   * inserting new rows, not when merging with existing rows under
   * `ignoreDuplicates: false`. This also only applies when doing bulk upserts.
   */
  upsert(e, { onConflict: t, ignoreDuplicates: s = !1, count: n, defaultToNull: i = !0 } = {}) {
    const a = "POST", l = [`resolution=${s ? "ignore" : "merge"}-duplicates`];
    if (t !== void 0 && this.url.searchParams.set("on_conflict", t), this.headers.Prefer && l.push(this.headers.Prefer), n && l.push(`count=${n}`), i || l.push("missing=default"), this.headers.Prefer = l.join(","), Array.isArray(e)) {
      const o = e.reduce((c, u) => c.concat(Object.keys(u)), []);
      if (o.length > 0) {
        const c = [...new Set(o)].map((u) => `"${u}"`);
        this.url.searchParams.set("columns", c.join(","));
      }
    }
    return new lt.default({
      method: a,
      url: this.url,
      headers: this.headers,
      schema: this.schema,
      body: e,
      fetch: this.fetch,
      allowEmpty: !1
    });
  }
  /**
   * Perform an UPDATE on the table or view.
   *
   * By default, updated rows are not returned. To return it, chain the call
   * with `.select()` after filters.
   *
   * @param values - The values to update with
   *
   * @param options - Named parameters
   *
   * @param options.count - Count algorithm to use to count updated rows.
   *
   * `"exact"`: Exact but slow count algorithm. Performs a `COUNT(*)` under the
   * hood.
   *
   * `"planned"`: Approximated but fast count algorithm. Uses the Postgres
   * statistics under the hood.
   *
   * `"estimated"`: Uses exact count for low numbers and planned count for high
   * numbers.
   */
  update(e, { count: t } = {}) {
    const s = "PATCH", n = [];
    return this.headers.Prefer && n.push(this.headers.Prefer), t && n.push(`count=${t}`), this.headers.Prefer = n.join(","), new lt.default({
      method: s,
      url: this.url,
      headers: this.headers,
      schema: this.schema,
      body: e,
      fetch: this.fetch,
      allowEmpty: !1
    });
  }
  /**
   * Perform a DELETE on the table or view.
   *
   * By default, deleted rows are not returned. To return it, chain the call
   * with `.select()` after filters.
   *
   * @param options - Named parameters
   *
   * @param options.count - Count algorithm to use to count deleted rows.
   *
   * `"exact"`: Exact but slow count algorithm. Performs a `COUNT(*)` under the
   * hood.
   *
   * `"planned"`: Approximated but fast count algorithm. Uses the Postgres
   * statistics under the hood.
   *
   * `"estimated"`: Uses exact count for low numbers and planned count for high
   * numbers.
   */
  delete({ count: e } = {}) {
    const t = "DELETE", s = [];
    return e && s.push(`count=${e}`), this.headers.Prefer && s.unshift(this.headers.Prefer), this.headers.Prefer = s.join(","), new lt.default({
      method: t,
      url: this.url,
      headers: this.headers,
      schema: this.schema,
      fetch: this.fetch,
      allowEmpty: !1
    });
  }
};
Lt.default = ai;
var Wt = {}, jt = {};
Object.defineProperty(jt, "__esModule", { value: !0 });
jt.version = void 0;
jt.version = "0.0.0-automated";
Object.defineProperty(Wt, "__esModule", { value: !0 });
Wt.DEFAULT_HEADERS = void 0;
const oi = jt;
Wt.DEFAULT_HEADERS = { "X-Client-Info": `postgrest-js/${oi.version}` };
var mr = Ee && Ee.__importDefault || function(r) {
  return r && r.__esModule ? r : { default: r };
};
Object.defineProperty(os, "__esModule", { value: !0 });
const li = mr(Lt), ci = mr(vt), ui = Wt;
let hi = class br {
  // TODO: Add back shouldThrowOnError once we figure out the typings
  /**
   * Creates a PostgREST client.
   *
   * @param url - URL of the PostgREST endpoint
   * @param options - Named parameters
   * @param options.headers - Custom headers
   * @param options.schema - Postgres schema to switch to
   * @param options.fetch - Custom fetch
   */
  constructor(e, { headers: t = {}, schema: s, fetch: n } = {}) {
    this.url = e, this.headers = Object.assign(Object.assign({}, ui.DEFAULT_HEADERS), t), this.schemaName = s, this.fetch = n;
  }
  /**
   * Perform a query on a table or a view.
   *
   * @param relation - The table or view name to query
   */
  from(e) {
    const t = new URL(`${this.url}/${e}`);
    return new li.default(t, {
      headers: Object.assign({}, this.headers),
      schema: this.schemaName,
      fetch: this.fetch
    });
  }
  /**
   * Select a schema to query or perform an function (rpc) call.
   *
   * The schema needs to be on the list of exposed schemas inside Supabase.
   *
   * @param schema - The schema to query
   */
  schema(e) {
    return new br(this.url, {
      headers: this.headers,
      schema: e,
      fetch: this.fetch
    });
  }
  /**
   * Perform a function call.
   *
   * @param fn - The function name to call
   * @param args - The arguments to pass to the function call
   * @param options - Named parameters
   * @param options.head - When set to `true`, `data` will not be returned.
   * Useful if you only need the count.
   * @param options.get - When set to `true`, the function will be called with
   * read-only access mode.
   * @param options.count - Count algorithm to use to count rows returned by the
   * function. Only applicable for [set-returning
   * functions](https://www.postgresql.org/docs/current/functions-srf.html).
   *
   * `"exact"`: Exact but slow count algorithm. Performs a `COUNT(*)` under the
   * hood.
   *
   * `"planned"`: Approximated but fast count algorithm. Uses the Postgres
   * statistics under the hood.
   *
   * `"estimated"`: Uses exact count for low numbers and planned count for high
   * numbers.
   */
  rpc(e, t = {}, { head: s = !1, get: n = !1, count: i } = {}) {
    let a;
    const l = new URL(`${this.url}/rpc/${e}`);
    let o;
    s || n ? (a = s ? "HEAD" : "GET", Object.entries(t).filter(([u, h]) => h !== void 0).map(([u, h]) => [u, Array.isArray(h) ? `{${h.join(",")}}` : `${h}`]).forEach(([u, h]) => {
      l.searchParams.append(u, h);
    })) : (a = "POST", o = t);
    const c = Object.assign({}, this.headers);
    return i && (c.Prefer = `count=${i}`), new ci.default({
      method: a,
      url: l,
      headers: c,
      schema: this.schemaName,
      body: o,
      fetch: this.fetch,
      allowEmpty: !1
    });
  }
};
os.default = hi;
var ot = Ee && Ee.__importDefault || function(r) {
  return r && r.__esModule ? r : { default: r };
};
Object.defineProperty(he, "__esModule", { value: !0 });
he.PostgrestError = he.PostgrestBuilder = he.PostgrestTransformBuilder = he.PostgrestFilterBuilder = he.PostgrestQueryBuilder = he.PostgrestClient = void 0;
const yr = ot(os);
he.PostgrestClient = yr.default;
const wr = ot(Lt);
he.PostgrestQueryBuilder = wr.default;
const Sr = ot(vt);
he.PostgrestFilterBuilder = Sr.default;
const Ir = ot(Dt);
he.PostgrestTransformBuilder = Ir.default;
const Ar = ot(Ut);
he.PostgrestBuilder = Ar.default;
const Or = ot(Vt);
he.PostgrestError = Or.default;
var di = he.default = {
  PostgrestClient: yr.default,
  PostgrestQueryBuilder: wr.default,
  PostgrestFilterBuilder: Sr.default,
  PostgrestTransformBuilder: Ir.default,
  PostgrestBuilder: Ar.default,
  PostgrestError: Or.default
};
const {
  PostgrestClient: fi,
  PostgrestQueryBuilder: vo,
  PostgrestFilterBuilder: mo,
  PostgrestTransformBuilder: bo,
  PostgrestBuilder: yo,
  PostgrestError: wo
} = di, _i = "2.11.2", gi = { "X-Client-Info": `realtime-js/${_i}` }, pi = "1.0.0", Cr = 1e4, Ei = 1e3;
var et;
(function(r) {
  r[r.connecting = 0] = "connecting", r[r.open = 1] = "open", r[r.closing = 2] = "closing", r[r.closed = 3] = "closed";
})(et || (et = {}));
var fe;
(function(r) {
  r.closed = "closed", r.errored = "errored", r.joined = "joined", r.joining = "joining", r.leaving = "leaving";
})(fe || (fe = {}));
var ye;
(function(r) {
  r.close = "phx_close", r.error = "phx_error", r.join = "phx_join", r.reply = "phx_reply", r.leave = "phx_leave", r.access_token = "access_token";
})(ye || (ye = {}));
var Yt;
(function(r) {
  r.websocket = "websocket";
})(Yt || (Yt = {}));
var Ne;
(function(r) {
  r.Connecting = "connecting", r.Open = "open", r.Closing = "closing", r.Closed = "closed";
})(Ne || (Ne = {}));
class vi {
  constructor() {
    this.HEADER_LENGTH = 1;
  }
  decode(e, t) {
    return e.constructor === ArrayBuffer ? t(this._binaryDecode(e)) : t(typeof e == "string" ? JSON.parse(e) : {});
  }
  _binaryDecode(e) {
    const t = new DataView(e), s = new TextDecoder();
    return this._decodeBroadcast(e, t, s);
  }
  _decodeBroadcast(e, t, s) {
    const n = t.getUint8(1), i = t.getUint8(2);
    let a = this.HEADER_LENGTH + 2;
    const l = s.decode(e.slice(a, a + n));
    a = a + n;
    const o = s.decode(e.slice(a, a + i));
    a = a + i;
    const c = JSON.parse(s.decode(e.slice(a, e.byteLength)));
    return { ref: null, topic: l, event: o, payload: c };
  }
}
class Tr {
  constructor(e, t) {
    this.callback = e, this.timerCalc = t, this.timer = void 0, this.tries = 0, this.callback = e, this.timerCalc = t;
  }
  reset() {
    this.tries = 0, clearTimeout(this.timer);
  }
  // Cancels any previous scheduleTimeout and schedules callback
  scheduleTimeout() {
    clearTimeout(this.timer), this.timer = setTimeout(() => {
      this.tries = this.tries + 1, this.callback();
    }, this.timerCalc(this.tries + 1));
  }
}
var ee;
(function(r) {
  r.abstime = "abstime", r.bool = "bool", r.date = "date", r.daterange = "daterange", r.float4 = "float4", r.float8 = "float8", r.int2 = "int2", r.int4 = "int4", r.int4range = "int4range", r.int8 = "int8", r.int8range = "int8range", r.json = "json", r.jsonb = "jsonb", r.money = "money", r.numeric = "numeric", r.oid = "oid", r.reltime = "reltime", r.text = "text", r.time = "time", r.timestamp = "timestamp", r.timestamptz = "timestamptz", r.timetz = "timetz", r.tsrange = "tsrange", r.tstzrange = "tstzrange";
})(ee || (ee = {}));
const Hs = (r, e, t = {}) => {
  var s;
  const n = (s = t.skipTypes) !== null && s !== void 0 ? s : [];
  return Object.keys(e).reduce((i, a) => (i[a] = mi(a, r, e, n), i), {});
}, mi = (r, e, t, s) => {
  const n = e.find((l) => l.name === r), i = n == null ? void 0 : n.type, a = t[r];
  return i && !s.includes(i) ? Rr(i, a) : Xt(a);
}, Rr = (r, e) => {
  if (r.charAt(0) === "_") {
    const t = r.slice(1, r.length);
    return Si(e, t);
  }
  switch (r) {
    case ee.bool:
      return bi(e);
    case ee.float4:
    case ee.float8:
    case ee.int2:
    case ee.int4:
    case ee.int8:
    case ee.numeric:
    case ee.oid:
      return yi(e);
    case ee.json:
    case ee.jsonb:
      return wi(e);
    case ee.timestamp:
      return Ii(e);
    case ee.abstime:
    case ee.date:
    case ee.daterange:
    case ee.int4range:
    case ee.int8range:
    case ee.money:
    case ee.reltime:
    case ee.text:
    case ee.time:
    case ee.timestamptz:
    case ee.timetz:
    case ee.tsrange:
    case ee.tstzrange:
      return Xt(e);
    default:
      return Xt(e);
  }
}, Xt = (r) => r, bi = (r) => {
  switch (r) {
    case "t":
      return !0;
    case "f":
      return !1;
    default:
      return r;
  }
}, yi = (r) => {
  if (typeof r == "string") {
    const e = parseFloat(r);
    if (!Number.isNaN(e))
      return e;
  }
  return r;
}, wi = (r) => {
  if (typeof r == "string")
    try {
      return JSON.parse(r);
    } catch (e) {
      return console.log(`JSON parse error: ${e}`), r;
    }
  return r;
}, Si = (r, e) => {
  if (typeof r != "string")
    return r;
  const t = r.length - 1, s = r[t];
  if (r[0] === "{" && s === "}") {
    let i;
    const a = r.slice(1, t);
    try {
      i = JSON.parse("[" + a + "]");
    } catch {
      i = a ? a.split(",") : [];
    }
    return i.map((l) => Rr(e, l));
  }
  return r;
}, Ii = (r) => typeof r == "string" ? r.replace(" ", "T") : r, kr = (r) => {
  let e = r;
  return e = e.replace(/^ws/i, "http"), e = e.replace(/(\/socket\/websocket|\/socket|\/websocket)\/?$/i, ""), e.replace(/\/+$/, "");
};
class Mt {
  /**
   * Initializes the Push
   *
   * @param channel The Channel
   * @param event The event, for example `"phx_join"`
   * @param payload The payload, for example `{user_id: 123}`
   * @param timeout The push timeout in milliseconds
   */
  constructor(e, t, s = {}, n = Cr) {
    this.channel = e, this.event = t, this.payload = s, this.timeout = n, this.sent = !1, this.timeoutTimer = void 0, this.ref = "", this.receivedResp = null, this.recHooks = [], this.refEvent = null;
  }
  resend(e) {
    this.timeout = e, this._cancelRefEvent(), this.ref = "", this.refEvent = null, this.receivedResp = null, this.sent = !1, this.send();
  }
  send() {
    this._hasReceived("timeout") || (this.startTimeout(), this.sent = !0, this.channel.socket.push({
      topic: this.channel.topic,
      event: this.event,
      payload: this.payload,
      ref: this.ref,
      join_ref: this.channel._joinRef()
    }));
  }
  updatePayload(e) {
    this.payload = Object.assign(Object.assign({}, this.payload), e);
  }
  receive(e, t) {
    var s;
    return this._hasReceived(e) && t((s = this.receivedResp) === null || s === void 0 ? void 0 : s.response), this.recHooks.push({ status: e, callback: t }), this;
  }
  startTimeout() {
    if (this.timeoutTimer)
      return;
    this.ref = this.channel.socket._makeRef(), this.refEvent = this.channel._replyEventName(this.ref);
    const e = (t) => {
      this._cancelRefEvent(), this._cancelTimeout(), this.receivedResp = t, this._matchReceive(t);
    };
    this.channel._on(this.refEvent, {}, e), this.timeoutTimer = setTimeout(() => {
      this.trigger("timeout", {});
    }, this.timeout);
  }
  trigger(e, t) {
    this.refEvent && this.channel._trigger(this.refEvent, { status: e, response: t });
  }
  destroy() {
    this._cancelRefEvent(), this._cancelTimeout();
  }
  _cancelRefEvent() {
    this.refEvent && this.channel._off(this.refEvent, {});
  }
  _cancelTimeout() {
    clearTimeout(this.timeoutTimer), this.timeoutTimer = void 0;
  }
  _matchReceive({ status: e, response: t }) {
    this.recHooks.filter((s) => s.status === e).forEach((s) => s.callback(t));
  }
  _hasReceived(e) {
    return this.receivedResp && this.receivedResp.status === e;
  }
}
var $s;
(function(r) {
  r.SYNC = "sync", r.JOIN = "join", r.LEAVE = "leave";
})($s || ($s = {}));
class dt {
  /**
   * Initializes the Presence.
   *
   * @param channel - The RealtimeChannel
   * @param opts - The options,
   *        for example `{events: {state: 'state', diff: 'diff'}}`
   */
  constructor(e, t) {
    this.channel = e, this.state = {}, this.pendingDiffs = [], this.joinRef = null, this.caller = {
      onJoin: () => {
      },
      onLeave: () => {
      },
      onSync: () => {
      }
    };
    const s = (t == null ? void 0 : t.events) || {
      state: "presence_state",
      diff: "presence_diff"
    };
    this.channel._on(s.state, {}, (n) => {
      const { onJoin: i, onLeave: a, onSync: l } = this.caller;
      this.joinRef = this.channel._joinRef(), this.state = dt.syncState(this.state, n, i, a), this.pendingDiffs.forEach((o) => {
        this.state = dt.syncDiff(this.state, o, i, a);
      }), this.pendingDiffs = [], l();
    }), this.channel._on(s.diff, {}, (n) => {
      const { onJoin: i, onLeave: a, onSync: l } = this.caller;
      this.inPendingSyncState() ? this.pendingDiffs.push(n) : (this.state = dt.syncDiff(this.state, n, i, a), l());
    }), this.onJoin((n, i, a) => {
      this.channel._trigger("presence", {
        event: "join",
        key: n,
        currentPresences: i,
        newPresences: a
      });
    }), this.onLeave((n, i, a) => {
      this.channel._trigger("presence", {
        event: "leave",
        key: n,
        currentPresences: i,
        leftPresences: a
      });
    }), this.onSync(() => {
      this.channel._trigger("presence", { event: "sync" });
    });
  }
  /**
   * Used to sync the list of presences on the server with the
   * client's state.
   *
   * An optional `onJoin` and `onLeave` callback can be provided to
   * react to changes in the client's local presences across
   * disconnects and reconnects with the server.
   *
   * @internal
   */
  static syncState(e, t, s, n) {
    const i = this.cloneDeep(e), a = this.transformState(t), l = {}, o = {};
    return this.map(i, (c, u) => {
      a[c] || (o[c] = u);
    }), this.map(a, (c, u) => {
      const h = i[c];
      if (h) {
        const d = u.map((w) => w.presence_ref), _ = h.map((w) => w.presence_ref), p = u.filter((w) => _.indexOf(w.presence_ref) < 0), v = h.filter((w) => d.indexOf(w.presence_ref) < 0);
        p.length > 0 && (l[c] = p), v.length > 0 && (o[c] = v);
      } else
        l[c] = u;
    }), this.syncDiff(i, { joins: l, leaves: o }, s, n);
  }
  /**
   * Used to sync a diff of presence join and leave events from the
   * server, as they happen.
   *
   * Like `syncState`, `syncDiff` accepts optional `onJoin` and
   * `onLeave` callbacks to react to a user joining or leaving from a
   * device.
   *
   * @internal
   */
  static syncDiff(e, t, s, n) {
    const { joins: i, leaves: a } = {
      joins: this.transformState(t.joins),
      leaves: this.transformState(t.leaves)
    };
    return s || (s = () => {
    }), n || (n = () => {
    }), this.map(i, (l, o) => {
      var c;
      const u = (c = e[l]) !== null && c !== void 0 ? c : [];
      if (e[l] = this.cloneDeep(o), u.length > 0) {
        const h = e[l].map((_) => _.presence_ref), d = u.filter((_) => h.indexOf(_.presence_ref) < 0);
        e[l].unshift(...d);
      }
      s(l, u, o);
    }), this.map(a, (l, o) => {
      let c = e[l];
      if (!c)
        return;
      const u = o.map((h) => h.presence_ref);
      c = c.filter((h) => u.indexOf(h.presence_ref) < 0), e[l] = c, n(l, c, o), c.length === 0 && delete e[l];
    }), e;
  }
  /** @internal */
  static map(e, t) {
    return Object.getOwnPropertyNames(e).map((s) => t(s, e[s]));
  }
  /**
   * Remove 'metas' key
   * Change 'phx_ref' to 'presence_ref'
   * Remove 'phx_ref' and 'phx_ref_prev'
   *
   * @example
   * // returns {
   *  abc123: [
   *    { presence_ref: '2', user_id: 1 },
   *    { presence_ref: '3', user_id: 2 }
   *  ]
   * }
   * RealtimePresence.transformState({
   *  abc123: {
   *    metas: [
   *      { phx_ref: '2', phx_ref_prev: '1' user_id: 1 },
   *      { phx_ref: '3', user_id: 2 }
   *    ]
   *  }
   * })
   *
   * @internal
   */
  static transformState(e) {
    return e = this.cloneDeep(e), Object.getOwnPropertyNames(e).reduce((t, s) => {
      const n = e[s];
      return "metas" in n ? t[s] = n.metas.map((i) => (i.presence_ref = i.phx_ref, delete i.phx_ref, delete i.phx_ref_prev, i)) : t[s] = n, t;
    }, {});
  }
  /** @internal */
  static cloneDeep(e) {
    return JSON.parse(JSON.stringify(e));
  }
  /** @internal */
  onJoin(e) {
    this.caller.onJoin = e;
  }
  /** @internal */
  onLeave(e) {
    this.caller.onLeave = e;
  }
  /** @internal */
  onSync(e) {
    this.caller.onSync = e;
  }
  /** @internal */
  inPendingSyncState() {
    return !this.joinRef || this.joinRef !== this.channel._joinRef();
  }
}
var Bs;
(function(r) {
  r.ALL = "*", r.INSERT = "INSERT", r.UPDATE = "UPDATE", r.DELETE = "DELETE";
})(Bs || (Bs = {}));
var Gs;
(function(r) {
  r.BROADCAST = "broadcast", r.PRESENCE = "presence", r.POSTGRES_CHANGES = "postgres_changes", r.SYSTEM = "system";
})(Gs || (Gs = {}));
var Oe;
(function(r) {
  r.SUBSCRIBED = "SUBSCRIBED", r.TIMED_OUT = "TIMED_OUT", r.CLOSED = "CLOSED", r.CHANNEL_ERROR = "CHANNEL_ERROR";
})(Oe || (Oe = {}));
class ls {
  constructor(e, t = { config: {} }, s) {
    this.topic = e, this.params = t, this.socket = s, this.bindings = {}, this.state = fe.closed, this.joinedOnce = !1, this.pushBuffer = [], this.subTopic = e.replace(/^realtime:/i, ""), this.params.config = Object.assign({
      broadcast: { ack: !1, self: !1 },
      presence: { key: "" },
      private: !1
    }, t.config), this.timeout = this.socket.timeout, this.joinPush = new Mt(this, ye.join, this.params, this.timeout), this.rejoinTimer = new Tr(() => this._rejoinUntilConnected(), this.socket.reconnectAfterMs), this.joinPush.receive("ok", () => {
      this.state = fe.joined, this.rejoinTimer.reset(), this.pushBuffer.forEach((n) => n.send()), this.pushBuffer = [];
    }), this._onClose(() => {
      this.rejoinTimer.reset(), this.socket.log("channel", `close ${this.topic} ${this._joinRef()}`), this.state = fe.closed, this.socket._remove(this);
    }), this._onError((n) => {
      this._isLeaving() || this._isClosed() || (this.socket.log("channel", `error ${this.topic}`, n), this.state = fe.errored, this.rejoinTimer.scheduleTimeout());
    }), this.joinPush.receive("timeout", () => {
      this._isJoining() && (this.socket.log("channel", `timeout ${this.topic}`, this.joinPush.timeout), this.state = fe.errored, this.rejoinTimer.scheduleTimeout());
    }), this._on(ye.reply, {}, (n, i) => {
      this._trigger(this._replyEventName(i), n);
    }), this.presence = new dt(this), this.broadcastEndpointURL = kr(this.socket.endPoint) + "/api/broadcast", this.private = this.params.config.private || !1;
  }
  /** Subscribe registers your client with the server */
  subscribe(e, t = this.timeout) {
    var s, n;
    if (this.socket.isConnected() || this.socket.connect(), this.joinedOnce)
      throw "tried to subscribe multiple times. 'subscribe' can only be called a single time per channel instance";
    {
      const { config: { broadcast: i, presence: a, private: l } } = this.params;
      this._onError((u) => e == null ? void 0 : e(Oe.CHANNEL_ERROR, u)), this._onClose(() => e == null ? void 0 : e(Oe.CLOSED));
      const o = {}, c = {
        broadcast: i,
        presence: a,
        postgres_changes: (n = (s = this.bindings.postgres_changes) === null || s === void 0 ? void 0 : s.map((u) => u.filter)) !== null && n !== void 0 ? n : [],
        private: l
      };
      this.socket.accessTokenValue && (o.access_token = this.socket.accessTokenValue), this.updateJoinPayload(Object.assign({ config: c }, o)), this.joinedOnce = !0, this._rejoin(t), this.joinPush.receive("ok", async ({ postgres_changes: u }) => {
        var h;
        if (this.socket.setAuth(), u === void 0) {
          e == null || e(Oe.SUBSCRIBED);
          return;
        } else {
          const d = this.bindings.postgres_changes, _ = (h = d == null ? void 0 : d.length) !== null && h !== void 0 ? h : 0, p = [];
          for (let v = 0; v < _; v++) {
            const w = d[v], { filter: { event: S, schema: A, table: y, filter: O } } = w, C = u && u[v];
            if (C && C.event === S && C.schema === A && C.table === y && C.filter === O)
              p.push(Object.assign(Object.assign({}, w), { id: C.id }));
            else {
              this.unsubscribe(), e == null || e(Oe.CHANNEL_ERROR, new Error("mismatch between server and client bindings for postgres changes"));
              return;
            }
          }
          this.bindings.postgres_changes = p, e && e(Oe.SUBSCRIBED);
          return;
        }
      }).receive("error", (u) => {
        e == null || e(Oe.CHANNEL_ERROR, new Error(JSON.stringify(Object.values(u).join(", ") || "error")));
      }).receive("timeout", () => {
        e == null || e(Oe.TIMED_OUT);
      });
    }
    return this;
  }
  presenceState() {
    return this.presence.state;
  }
  async track(e, t = {}) {
    return await this.send({
      type: "presence",
      event: "track",
      payload: e
    }, t.timeout || this.timeout);
  }
  async untrack(e = {}) {
    return await this.send({
      type: "presence",
      event: "untrack"
    }, e);
  }
  on(e, t, s) {
    return this._on(e, t, s);
  }
  /**
   * Sends a message into the channel.
   *
   * @param args Arguments to send to channel
   * @param args.type The type of event to send
   * @param args.event The name of the event being sent
   * @param args.payload Payload to be sent
   * @param opts Options to be used during the send process
   */
  async send(e, t = {}) {
    var s, n;
    if (!this._canPush() && e.type === "broadcast") {
      const { event: i, payload: a } = e, o = {
        method: "POST",
        headers: {
          Authorization: this.socket.accessTokenValue ? `Bearer ${this.socket.accessTokenValue}` : "",
          apikey: this.socket.apiKey ? this.socket.apiKey : "",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          messages: [
            {
              topic: this.subTopic,
              event: i,
              payload: a,
              private: this.private
            }
          ]
        })
      };
      try {
        const c = await this._fetchWithTimeout(this.broadcastEndpointURL, o, (s = t.timeout) !== null && s !== void 0 ? s : this.timeout);
        return await ((n = c.body) === null || n === void 0 ? void 0 : n.cancel()), c.ok ? "ok" : "error";
      } catch (c) {
        return c.name === "AbortError" ? "timed out" : "error";
      }
    } else
      return new Promise((i) => {
        var a, l, o;
        const c = this._push(e.type, e, t.timeout || this.timeout);
        e.type === "broadcast" && !(!((o = (l = (a = this.params) === null || a === void 0 ? void 0 : a.config) === null || l === void 0 ? void 0 : l.broadcast) === null || o === void 0) && o.ack) && i("ok"), c.receive("ok", () => i("ok")), c.receive("error", () => i("error")), c.receive("timeout", () => i("timed out"));
      });
  }
  updateJoinPayload(e) {
    this.joinPush.updatePayload(e);
  }
  /**
   * Leaves the channel.
   *
   * Unsubscribes from server events, and instructs channel to terminate on server.
   * Triggers onClose() hooks.
   *
   * To receive leave acknowledgements, use the a `receive` hook to bind to the server ack, ie:
   * channel.unsubscribe().receive("ok", () => alert("left!") )
   */
  unsubscribe(e = this.timeout) {
    this.state = fe.leaving;
    const t = () => {
      this.socket.log("channel", `leave ${this.topic}`), this._trigger(ye.close, "leave", this._joinRef());
    };
    return this.rejoinTimer.reset(), this.joinPush.destroy(), new Promise((s) => {
      const n = new Mt(this, ye.leave, {}, e);
      n.receive("ok", () => {
        t(), s("ok");
      }).receive("timeout", () => {
        t(), s("timed out");
      }).receive("error", () => {
        s("error");
      }), n.send(), this._canPush() || n.trigger("ok", {});
    });
  }
  /** @internal */
  async _fetchWithTimeout(e, t, s) {
    const n = new AbortController(), i = setTimeout(() => n.abort(), s), a = await this.socket.fetch(e, Object.assign(Object.assign({}, t), { signal: n.signal }));
    return clearTimeout(i), a;
  }
  /** @internal */
  _push(e, t, s = this.timeout) {
    if (!this.joinedOnce)
      throw `tried to push '${e}' to '${this.topic}' before joining. Use channel.subscribe() before pushing events`;
    let n = new Mt(this, e, t, s);
    return this._canPush() ? n.send() : (n.startTimeout(), this.pushBuffer.push(n)), n;
  }
  /**
   * Overridable message hook
   *
   * Receives all events for specialized message handling before dispatching to the channel callbacks.
   * Must return the payload, modified or unmodified.
   *
   * @internal
   */
  _onMessage(e, t, s) {
    return t;
  }
  /** @internal */
  _isMember(e) {
    return this.topic === e;
  }
  /** @internal */
  _joinRef() {
    return this.joinPush.ref;
  }
  /** @internal */
  _trigger(e, t, s) {
    var n, i;
    const a = e.toLocaleLowerCase(), { close: l, error: o, leave: c, join: u } = ye;
    if (s && [l, o, c, u].indexOf(a) >= 0 && s !== this._joinRef())
      return;
    let d = this._onMessage(a, t, s);
    if (t && !d)
      throw "channel onMessage callbacks must return the payload, modified or unmodified";
    ["insert", "update", "delete"].includes(a) ? (n = this.bindings.postgres_changes) === null || n === void 0 || n.filter((_) => {
      var p, v, w;
      return ((p = _.filter) === null || p === void 0 ? void 0 : p.event) === "*" || ((w = (v = _.filter) === null || v === void 0 ? void 0 : v.event) === null || w === void 0 ? void 0 : w.toLocaleLowerCase()) === a;
    }).map((_) => _.callback(d, s)) : (i = this.bindings[a]) === null || i === void 0 || i.filter((_) => {
      var p, v, w, S, A, y;
      if (["broadcast", "presence", "postgres_changes"].includes(a))
        if ("id" in _) {
          const O = _.id, C = (p = _.filter) === null || p === void 0 ? void 0 : p.event;
          return O && ((v = t.ids) === null || v === void 0 ? void 0 : v.includes(O)) && (C === "*" || (C == null ? void 0 : C.toLocaleLowerCase()) === ((w = t.data) === null || w === void 0 ? void 0 : w.type.toLocaleLowerCase()));
        } else {
          const O = (A = (S = _ == null ? void 0 : _.filter) === null || S === void 0 ? void 0 : S.event) === null || A === void 0 ? void 0 : A.toLocaleLowerCase();
          return O === "*" || O === ((y = t == null ? void 0 : t.event) === null || y === void 0 ? void 0 : y.toLocaleLowerCase());
        }
      else
        return _.type.toLocaleLowerCase() === a;
    }).map((_) => {
      if (typeof d == "object" && "ids" in d) {
        const p = d.data, { schema: v, table: w, commit_timestamp: S, type: A, errors: y } = p;
        d = Object.assign(Object.assign({}, {
          schema: v,
          table: w,
          commit_timestamp: S,
          eventType: A,
          new: {},
          old: {},
          errors: y
        }), this._getPayloadRecords(p));
      }
      _.callback(d, s);
    });
  }
  /** @internal */
  _isClosed() {
    return this.state === fe.closed;
  }
  /** @internal */
  _isJoined() {
    return this.state === fe.joined;
  }
  /** @internal */
  _isJoining() {
    return this.state === fe.joining;
  }
  /** @internal */
  _isLeaving() {
    return this.state === fe.leaving;
  }
  /** @internal */
  _replyEventName(e) {
    return `chan_reply_${e}`;
  }
  /** @internal */
  _on(e, t, s) {
    const n = e.toLocaleLowerCase(), i = {
      type: n,
      filter: t,
      callback: s
    };
    return this.bindings[n] ? this.bindings[n].push(i) : this.bindings[n] = [i], this;
  }
  /** @internal */
  _off(e, t) {
    const s = e.toLocaleLowerCase();
    return this.bindings[s] = this.bindings[s].filter((n) => {
      var i;
      return !(((i = n.type) === null || i === void 0 ? void 0 : i.toLocaleLowerCase()) === s && ls.isEqual(n.filter, t));
    }), this;
  }
  /** @internal */
  static isEqual(e, t) {
    if (Object.keys(e).length !== Object.keys(t).length)
      return !1;
    for (const s in e)
      if (e[s] !== t[s])
        return !1;
    return !0;
  }
  /** @internal */
  _rejoinUntilConnected() {
    this.rejoinTimer.scheduleTimeout(), this.socket.isConnected() && this._rejoin();
  }
  /**
   * Registers a callback that will be executed when the channel closes.
   *
   * @internal
   */
  _onClose(e) {
    this._on(ye.close, {}, e);
  }
  /**
   * Registers a callback that will be executed when the channel encounteres an error.
   *
   * @internal
   */
  _onError(e) {
    this._on(ye.error, {}, (t) => e(t));
  }
  /**
   * Returns `true` if the socket is connected and the channel has been joined.
   *
   * @internal
   */
  _canPush() {
    return this.socket.isConnected() && this._isJoined();
  }
  /** @internal */
  _rejoin(e = this.timeout) {
    this._isLeaving() || (this.socket._leaveOpenTopic(this.topic), this.state = fe.joining, this.joinPush.resend(e));
  }
  /** @internal */
  _getPayloadRecords(e) {
    const t = {
      new: {},
      old: {}
    };
    return (e.type === "INSERT" || e.type === "UPDATE") && (t.new = Hs(e.columns, e.record)), (e.type === "UPDATE" || e.type === "DELETE") && (t.old = Hs(e.columns, e.old_record)), t;
  }
}
const Ai = () => {
}, Oi = typeof WebSocket < "u", Ci = `
  addEventListener("message", (e) => {
    if (e.data.event === "start") {
      setInterval(() => postMessage({ event: "keepAlive" }), e.data.interval);
    }
  });`;
class Ti {
  /**
   * Initializes the Socket.
   *
   * @param endPoint The string WebSocket endpoint, ie, "ws://example.com/socket", "wss://example.com", "/socket" (inherited host & protocol)
   * @param httpEndpoint The string HTTP endpoint, ie, "https://example.com", "/" (inherited host & protocol)
   * @param options.transport The Websocket Transport, for example WebSocket.
   * @param options.timeout The default timeout in milliseconds to trigger push timeouts.
   * @param options.params The optional params to pass when connecting.
   * @param options.headers The optional headers to pass when connecting.
   * @param options.heartbeatIntervalMs The millisec interval to send a heartbeat message.
   * @param options.logger The optional function for specialized logging, ie: logger: (kind, msg, data) => { console.log(`${kind}: ${msg}`, data) }
   * @param options.encode The function to encode outgoing messages. Defaults to JSON: (payload, callback) => callback(JSON.stringify(payload))
   * @param options.decode The function to decode incoming messages. Defaults to Serializer's decode.
   * @param options.reconnectAfterMs he optional function that returns the millsec reconnect interval. Defaults to stepped backoff off.
   * @param options.worker Use Web Worker to set a side flow. Defaults to false.
   * @param options.workerUrl The URL of the worker script. Defaults to https://realtime.supabase.com/worker.js that includes a heartbeat event call to keep the connection alive.
   */
  constructor(e, t) {
    var s;
    this.accessTokenValue = null, this.apiKey = null, this.channels = [], this.endPoint = "", this.httpEndpoint = "", this.headers = gi, this.params = {}, this.timeout = Cr, this.heartbeatIntervalMs = 3e4, this.heartbeatTimer = void 0, this.pendingHeartbeatRef = null, this.ref = 0, this.logger = Ai, this.conn = null, this.sendBuffer = [], this.serializer = new vi(), this.stateChangeCallbacks = {
      open: [],
      close: [],
      error: [],
      message: []
    }, this.accessToken = null, this._resolveFetch = (i) => {
      let a;
      return i ? a = i : typeof fetch > "u" ? a = (...l) => Promise.resolve().then(() => at).then(({ default: o }) => o(...l)) : a = fetch, (...l) => a(...l);
    }, this.endPoint = `${e}/${Yt.websocket}`, this.httpEndpoint = kr(e), t != null && t.transport ? this.transport = t.transport : this.transport = null, t != null && t.params && (this.params = t.params), t != null && t.headers && (this.headers = Object.assign(Object.assign({}, this.headers), t.headers)), t != null && t.timeout && (this.timeout = t.timeout), t != null && t.logger && (this.logger = t.logger), t != null && t.heartbeatIntervalMs && (this.heartbeatIntervalMs = t.heartbeatIntervalMs);
    const n = (s = t == null ? void 0 : t.params) === null || s === void 0 ? void 0 : s.apikey;
    if (n && (this.accessTokenValue = n, this.apiKey = n), this.reconnectAfterMs = t != null && t.reconnectAfterMs ? t.reconnectAfterMs : (i) => [1e3, 2e3, 5e3, 1e4][i - 1] || 1e4, this.encode = t != null && t.encode ? t.encode : (i, a) => a(JSON.stringify(i)), this.decode = t != null && t.decode ? t.decode : this.serializer.decode.bind(this.serializer), this.reconnectTimer = new Tr(async () => {
      this.disconnect(), this.connect();
    }, this.reconnectAfterMs), this.fetch = this._resolveFetch(t == null ? void 0 : t.fetch), t != null && t.worker) {
      if (typeof window < "u" && !window.Worker)
        throw new Error("Web Worker is not supported");
      this.worker = (t == null ? void 0 : t.worker) || !1, this.workerUrl = t == null ? void 0 : t.workerUrl;
    }
    this.accessToken = (t == null ? void 0 : t.accessToken) || null;
  }
  /**
   * Connects the socket, unless already connected.
   */
  connect() {
    if (!this.conn) {
      if (this.transport) {
        this.conn = new this.transport(this.endpointURL(), void 0, {
          headers: this.headers
        });
        return;
      }
      if (Oi) {
        this.conn = new WebSocket(this.endpointURL()), this.setupConnection();
        return;
      }
      this.conn = new Ri(this.endpointURL(), void 0, {
        close: () => {
          this.conn = null;
        }
      }), import("./browser-MVJaYfKS.js").then((e) => e.b).then(({ default: e }) => {
        this.conn = new e(this.endpointURL(), void 0, {
          headers: this.headers
        }), this.setupConnection();
      });
    }
  }
  /**
   * Returns the URL of the websocket.
   * @returns string The URL of the websocket.
   */
  endpointURL() {
    return this._appendParams(this.endPoint, Object.assign({}, this.params, { vsn: pi }));
  }
  /**
   * Disconnects the socket.
   *
   * @param code A numeric status code to send on disconnect.
   * @param reason A custom reason for the disconnect.
   */
  disconnect(e, t) {
    this.conn && (this.conn.onclose = function() {
    }, e ? this.conn.close(e, t ?? "") : this.conn.close(), this.conn = null, this.heartbeatTimer && clearInterval(this.heartbeatTimer), this.reconnectTimer.reset());
  }
  /**
   * Returns all created channels
   */
  getChannels() {
    return this.channels;
  }
  /**
   * Unsubscribes and removes a single channel
   * @param channel A RealtimeChannel instance
   */
  async removeChannel(e) {
    const t = await e.unsubscribe();
    return this.channels.length === 0 && this.disconnect(), t;
  }
  /**
   * Unsubscribes and removes all channels
   */
  async removeAllChannels() {
    const e = await Promise.all(this.channels.map((t) => t.unsubscribe()));
    return this.disconnect(), e;
  }
  /**
   * Logs the message.
   *
   * For customized logging, `this.logger` can be overridden.
   */
  log(e, t, s) {
    this.logger(e, t, s);
  }
  /**
   * Returns the current state of the socket.
   */
  connectionState() {
    switch (this.conn && this.conn.readyState) {
      case et.connecting:
        return Ne.Connecting;
      case et.open:
        return Ne.Open;
      case et.closing:
        return Ne.Closing;
      default:
        return Ne.Closed;
    }
  }
  /**
   * Returns `true` is the connection is open.
   */
  isConnected() {
    return this.connectionState() === Ne.Open;
  }
  channel(e, t = { config: {} }) {
    const s = new ls(`realtime:${e}`, t, this);
    return this.channels.push(s), s;
  }
  /**
   * Push out a message if the socket is connected.
   *
   * If the socket is not connected, the message gets enqueued within a local buffer, and sent out when a connection is next established.
   */
  push(e) {
    const { topic: t, event: s, payload: n, ref: i } = e, a = () => {
      this.encode(e, (l) => {
        var o;
        (o = this.conn) === null || o === void 0 || o.send(l);
      });
    };
    this.log("push", `${t} ${s} (${i})`, n), this.isConnected() ? a() : this.sendBuffer.push(a);
  }
  /**
   * Sets the JWT access token used for channel subscription authorization and Realtime RLS.
   *
   * If param is null it will use the `accessToken` callback function or the token set on the client.
   *
   * On callback used, it will set the value of the token internal to the client.
   *
   * @param token A JWT string to override the token set on the client.
   */
  async setAuth(e = null) {
    let t = e || this.accessToken && await this.accessToken() || this.accessTokenValue;
    if (t) {
      let s = null;
      try {
        s = JSON.parse(atob(t.split(".")[1]));
      } catch {
      }
      if (s && s.exp && !(Math.floor(Date.now() / 1e3) - s.exp < 0))
        return this.log("auth", `InvalidJWTToken: Invalid value for JWT claim "exp" with value ${s.exp}`), Promise.reject(`InvalidJWTToken: Invalid value for JWT claim "exp" with value ${s.exp}`);
      this.accessTokenValue = t, this.channels.forEach((n) => {
        t && n.updateJoinPayload({ access_token: t }), n.joinedOnce && n._isJoined() && n._push(ye.access_token, {
          access_token: t
        });
      });
    }
  }
  /**
   * Sends a heartbeat message if the socket is connected.
   */
  async sendHeartbeat() {
    var e;
    if (this.isConnected()) {
      if (this.pendingHeartbeatRef) {
        this.pendingHeartbeatRef = null, this.log("transport", "heartbeat timeout. Attempting to re-establish connection"), (e = this.conn) === null || e === void 0 || e.close(Ei, "hearbeat timeout");
        return;
      }
      this.pendingHeartbeatRef = this._makeRef(), this.push({
        topic: "phoenix",
        event: "heartbeat",
        payload: {},
        ref: this.pendingHeartbeatRef
      }), this.setAuth();
    }
  }
  /**
   * Flushes send buffer
   */
  flushSendBuffer() {
    this.isConnected() && this.sendBuffer.length > 0 && (this.sendBuffer.forEach((e) => e()), this.sendBuffer = []);
  }
  /**
   * Return the next message ref, accounting for overflows
   *
   * @internal
   */
  _makeRef() {
    let e = this.ref + 1;
    return e === this.ref ? this.ref = 0 : this.ref = e, this.ref.toString();
  }
  /**
   * Unsubscribe from channels with the specified topic.
   *
   * @internal
   */
  _leaveOpenTopic(e) {
    let t = this.channels.find((s) => s.topic === e && (s._isJoined() || s._isJoining()));
    t && (this.log("transport", `leaving duplicate topic "${e}"`), t.unsubscribe());
  }
  /**
   * Removes a subscription from the socket.
   *
   * @param channel An open subscription.
   *
   * @internal
   */
  _remove(e) {
    this.channels = this.channels.filter((t) => t._joinRef() !== e._joinRef());
  }
  /**
   * Sets up connection handlers.
   *
   * @internal
   */
  setupConnection() {
    this.conn && (this.conn.binaryType = "arraybuffer", this.conn.onopen = () => this._onConnOpen(), this.conn.onerror = (e) => this._onConnError(e), this.conn.onmessage = (e) => this._onConnMessage(e), this.conn.onclose = (e) => this._onConnClose(e));
  }
  /** @internal */
  _onConnMessage(e) {
    this.decode(e.data, (t) => {
      let { topic: s, event: n, payload: i, ref: a } = t;
      a && a === this.pendingHeartbeatRef && (this.pendingHeartbeatRef = null), this.log("receive", `${i.status || ""} ${s} ${n} ${a && "(" + a + ")" || ""}`, i), this.channels.filter((l) => l._isMember(s)).forEach((l) => l._trigger(n, i, a)), this.stateChangeCallbacks.message.forEach((l) => l(t));
    });
  }
  /** @internal */
  async _onConnOpen() {
    if (this.log("transport", `connected to ${this.endpointURL()}`), this.flushSendBuffer(), this.reconnectTimer.reset(), !this.worker)
      this.heartbeatTimer && clearInterval(this.heartbeatTimer), this.heartbeatTimer = setInterval(() => this.sendHeartbeat(), this.heartbeatIntervalMs);
    else {
      this.workerUrl ? this.log("worker", `starting worker for from ${this.workerUrl}`) : this.log("worker", "starting default worker");
      const e = this._workerObjectUrl(this.workerUrl);
      this.workerRef = new Worker(e), this.workerRef.onerror = (t) => {
        this.log("worker", "worker error", t.message), this.workerRef.terminate();
      }, this.workerRef.onmessage = (t) => {
        t.data.event === "keepAlive" && this.sendHeartbeat();
      }, this.workerRef.postMessage({
        event: "start",
        interval: this.heartbeatIntervalMs
      });
    }
    this.stateChangeCallbacks.open.forEach((e) => e());
  }
  /** @internal */
  _onConnClose(e) {
    this.log("transport", "close", e), this._triggerChanError(), this.heartbeatTimer && clearInterval(this.heartbeatTimer), this.reconnectTimer.scheduleTimeout(), this.stateChangeCallbacks.close.forEach((t) => t(e));
  }
  /** @internal */
  _onConnError(e) {
    this.log("transport", e.message), this._triggerChanError(), this.stateChangeCallbacks.error.forEach((t) => t(e));
  }
  /** @internal */
  _triggerChanError() {
    this.channels.forEach((e) => e._trigger(ye.error));
  }
  /** @internal */
  _appendParams(e, t) {
    if (Object.keys(t).length === 0)
      return e;
    const s = e.match(/\?/) ? "&" : "?", n = new URLSearchParams(t);
    return `${e}${s}${n}`;
  }
  _workerObjectUrl(e) {
    let t;
    if (e)
      t = e;
    else {
      const s = new Blob([Ci], { type: "application/javascript" });
      t = URL.createObjectURL(s);
    }
    return t;
  }
}
class Ri {
  constructor(e, t, s) {
    this.binaryType = "arraybuffer", this.onclose = () => {
    }, this.onerror = () => {
    }, this.onmessage = () => {
    }, this.onopen = () => {
    }, this.readyState = et.connecting, this.send = () => {
    }, this.url = null, this.url = e, this.close = s.close;
  }
}
class cs extends Error {
  constructor(e) {
    super(e), this.__isStorageError = !0, this.name = "StorageError";
  }
}
function oe(r) {
  return typeof r == "object" && r !== null && "__isStorageError" in r;
}
class ki extends cs {
  constructor(e, t) {
    super(e), this.name = "StorageApiError", this.status = t;
  }
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      status: this.status
    };
  }
}
class Qt extends cs {
  constructor(e, t) {
    super(e), this.name = "StorageUnknownError", this.originalError = t;
  }
}
var Pi = function(r, e, t, s) {
  function n(i) {
    return i instanceof t ? i : new t(function(a) {
      a(i);
    });
  }
  return new (t || (t = Promise))(function(i, a) {
    function l(u) {
      try {
        c(s.next(u));
      } catch (h) {
        a(h);
      }
    }
    function o(u) {
      try {
        c(s.throw(u));
      } catch (h) {
        a(h);
      }
    }
    function c(u) {
      u.done ? i(u.value) : n(u.value).then(l, o);
    }
    c((s = s.apply(r, e || [])).next());
  });
};
const Pr = (r) => {
  let e;
  return r ? e = r : typeof fetch > "u" ? e = (...t) => Promise.resolve().then(() => at).then(({ default: s }) => s(...t)) : e = fetch, (...t) => e(...t);
}, Li = () => Pi(void 0, void 0, void 0, function* () {
  return typeof Response > "u" ? (yield Promise.resolve().then(() => at)).Response : Response;
}), Zt = (r) => {
  if (Array.isArray(r))
    return r.map((t) => Zt(t));
  if (typeof r == "function" || r !== Object(r))
    return r;
  const e = {};
  return Object.entries(r).forEach(([t, s]) => {
    const n = t.replace(/([-_][a-z])/gi, (i) => i.toUpperCase().replace(/[-_]/g, ""));
    e[n] = Zt(s);
  }), e;
};
var Me = function(r, e, t, s) {
  function n(i) {
    return i instanceof t ? i : new t(function(a) {
      a(i);
    });
  }
  return new (t || (t = Promise))(function(i, a) {
    function l(u) {
      try {
        c(s.next(u));
      } catch (h) {
        a(h);
      }
    }
    function o(u) {
      try {
        c(s.throw(u));
      } catch (h) {
        a(h);
      }
    }
    function c(u) {
      u.done ? i(u.value) : n(u.value).then(l, o);
    }
    c((s = s.apply(r, e || [])).next());
  });
};
const Ht = (r) => r.msg || r.message || r.error_description || r.error || JSON.stringify(r), Di = (r, e, t) => Me(void 0, void 0, void 0, function* () {
  const s = yield Li();
  r instanceof s && !(t != null && t.noResolveJson) ? r.json().then((n) => {
    e(new ki(Ht(n), r.status || 500));
  }).catch((n) => {
    e(new Qt(Ht(n), n));
  }) : e(new Qt(Ht(r), r));
}), Ui = (r, e, t, s) => {
  const n = { method: r, headers: (e == null ? void 0 : e.headers) || {} };
  return r === "GET" ? n : (n.headers = Object.assign({ "Content-Type": "application/json" }, e == null ? void 0 : e.headers), s && (n.body = JSON.stringify(s)), Object.assign(Object.assign({}, n), t));
};
function mt(r, e, t, s, n, i) {
  return Me(this, void 0, void 0, function* () {
    return new Promise((a, l) => {
      r(t, Ui(e, s, n, i)).then((o) => {
        if (!o.ok)
          throw o;
        return s != null && s.noResolveJson ? o : o.json();
      }).then((o) => a(o)).catch((o) => Di(o, l, s));
    });
  });
}
function Tt(r, e, t, s) {
  return Me(this, void 0, void 0, function* () {
    return mt(r, "GET", e, t, s);
  });
}
function Re(r, e, t, s, n) {
  return Me(this, void 0, void 0, function* () {
    return mt(r, "POST", e, s, n, t);
  });
}
function Vi(r, e, t, s, n) {
  return Me(this, void 0, void 0, function* () {
    return mt(r, "PUT", e, s, n, t);
  });
}
function Wi(r, e, t, s) {
  return Me(this, void 0, void 0, function* () {
    return mt(r, "HEAD", e, Object.assign(Object.assign({}, t), { noResolveJson: !0 }), s);
  });
}
function Lr(r, e, t, s, n) {
  return Me(this, void 0, void 0, function* () {
    return mt(r, "DELETE", e, s, n, t);
  });
}
var ue = function(r, e, t, s) {
  function n(i) {
    return i instanceof t ? i : new t(function(a) {
      a(i);
    });
  }
  return new (t || (t = Promise))(function(i, a) {
    function l(u) {
      try {
        c(s.next(u));
      } catch (h) {
        a(h);
      }
    }
    function o(u) {
      try {
        c(s.throw(u));
      } catch (h) {
        a(h);
      }
    }
    function c(u) {
      u.done ? i(u.value) : n(u.value).then(l, o);
    }
    c((s = s.apply(r, e || [])).next());
  });
};
const ji = {
  limit: 100,
  offset: 0,
  sortBy: {
    column: "name",
    order: "asc"
  }
}, qs = {
  cacheControl: "3600",
  contentType: "text/plain;charset=UTF-8",
  upsert: !1
};
class Ni {
  constructor(e, t = {}, s, n) {
    this.url = e, this.headers = t, this.bucketId = s, this.fetch = Pr(n);
  }
  /**
   * Uploads a file to an existing bucket or replaces an existing file at the specified path with a new one.
   *
   * @param method HTTP method.
   * @param path The relative file path. Should be of the format `folder/subfolder/filename.png`. The bucket must already exist before attempting to upload.
   * @param fileBody The body of the file to be stored in the bucket.
   */
  uploadOrUpdate(e, t, s, n) {
    return ue(this, void 0, void 0, function* () {
      try {
        let i;
        const a = Object.assign(Object.assign({}, qs), n);
        let l = Object.assign(Object.assign({}, this.headers), e === "POST" && { "x-upsert": String(a.upsert) });
        const o = a.metadata;
        typeof Blob < "u" && s instanceof Blob ? (i = new FormData(), i.append("cacheControl", a.cacheControl), o && i.append("metadata", this.encodeMetadata(o)), i.append("", s)) : typeof FormData < "u" && s instanceof FormData ? (i = s, i.append("cacheControl", a.cacheControl), o && i.append("metadata", this.encodeMetadata(o))) : (i = s, l["cache-control"] = `max-age=${a.cacheControl}`, l["content-type"] = a.contentType, o && (l["x-metadata"] = this.toBase64(this.encodeMetadata(o)))), n != null && n.headers && (l = Object.assign(Object.assign({}, l), n.headers));
        const c = this._removeEmptyFolders(t), u = this._getFinalPath(c), h = yield this.fetch(`${this.url}/object/${u}`, Object.assign({ method: e, body: i, headers: l }, a != null && a.duplex ? { duplex: a.duplex } : {})), d = yield h.json();
        return h.ok ? {
          data: { path: c, id: d.Id, fullPath: d.Key },
          error: null
        } : { data: null, error: d };
      } catch (i) {
        if (oe(i))
          return { data: null, error: i };
        throw i;
      }
    });
  }
  /**
   * Uploads a file to an existing bucket.
   *
   * @param path The file path, including the file name. Should be of the format `folder/subfolder/filename.png`. The bucket must already exist before attempting to upload.
   * @param fileBody The body of the file to be stored in the bucket.
   */
  upload(e, t, s) {
    return ue(this, void 0, void 0, function* () {
      return this.uploadOrUpdate("POST", e, t, s);
    });
  }
  /**
   * Upload a file with a token generated from `createSignedUploadUrl`.
   * @param path The file path, including the file name. Should be of the format `folder/subfolder/filename.png`. The bucket must already exist before attempting to upload.
   * @param token The token generated from `createSignedUploadUrl`
   * @param fileBody The body of the file to be stored in the bucket.
   */
  uploadToSignedUrl(e, t, s, n) {
    return ue(this, void 0, void 0, function* () {
      const i = this._removeEmptyFolders(e), a = this._getFinalPath(i), l = new URL(this.url + `/object/upload/sign/${a}`);
      l.searchParams.set("token", t);
      try {
        let o;
        const c = Object.assign({ upsert: qs.upsert }, n), u = Object.assign(Object.assign({}, this.headers), { "x-upsert": String(c.upsert) });
        typeof Blob < "u" && s instanceof Blob ? (o = new FormData(), o.append("cacheControl", c.cacheControl), o.append("", s)) : typeof FormData < "u" && s instanceof FormData ? (o = s, o.append("cacheControl", c.cacheControl)) : (o = s, u["cache-control"] = `max-age=${c.cacheControl}`, u["content-type"] = c.contentType);
        const h = yield this.fetch(l.toString(), {
          method: "PUT",
          body: o,
          headers: u
        }), d = yield h.json();
        return h.ok ? {
          data: { path: i, fullPath: d.Key },
          error: null
        } : { data: null, error: d };
      } catch (o) {
        if (oe(o))
          return { data: null, error: o };
        throw o;
      }
    });
  }
  /**
   * Creates a signed upload URL.
   * Signed upload URLs can be used to upload files to the bucket without further authentication.
   * They are valid for 2 hours.
   * @param path The file path, including the current file name. For example `folder/image.png`.
   * @param options.upsert If set to true, allows the file to be overwritten if it already exists.
   */
  createSignedUploadUrl(e, t) {
    return ue(this, void 0, void 0, function* () {
      try {
        let s = this._getFinalPath(e);
        const n = Object.assign({}, this.headers);
        t != null && t.upsert && (n["x-upsert"] = "true");
        const i = yield Re(this.fetch, `${this.url}/object/upload/sign/${s}`, {}, { headers: n }), a = new URL(this.url + i.url), l = a.searchParams.get("token");
        if (!l)
          throw new cs("No token returned by API");
        return { data: { signedUrl: a.toString(), path: e, token: l }, error: null };
      } catch (s) {
        if (oe(s))
          return { data: null, error: s };
        throw s;
      }
    });
  }
  /**
   * Replaces an existing file at the specified path with a new one.
   *
   * @param path The relative file path. Should be of the format `folder/subfolder/filename.png`. The bucket must already exist before attempting to update.
   * @param fileBody The body of the file to be stored in the bucket.
   */
  update(e, t, s) {
    return ue(this, void 0, void 0, function* () {
      return this.uploadOrUpdate("PUT", e, t, s);
    });
  }
  /**
   * Moves an existing file to a new path in the same bucket.
   *
   * @param fromPath The original file path, including the current file name. For example `folder/image.png`.
   * @param toPath The new file path, including the new file name. For example `folder/image-new.png`.
   * @param options The destination options.
   */
  move(e, t, s) {
    return ue(this, void 0, void 0, function* () {
      try {
        return { data: yield Re(this.fetch, `${this.url}/object/move`, {
          bucketId: this.bucketId,
          sourceKey: e,
          destinationKey: t,
          destinationBucket: s == null ? void 0 : s.destinationBucket
        }, { headers: this.headers }), error: null };
      } catch (n) {
        if (oe(n))
          return { data: null, error: n };
        throw n;
      }
    });
  }
  /**
   * Copies an existing file to a new path in the same bucket.
   *
   * @param fromPath The original file path, including the current file name. For example `folder/image.png`.
   * @param toPath The new file path, including the new file name. For example `folder/image-copy.png`.
   * @param options The destination options.
   */
  copy(e, t, s) {
    return ue(this, void 0, void 0, function* () {
      try {
        return { data: { path: (yield Re(this.fetch, `${this.url}/object/copy`, {
          bucketId: this.bucketId,
          sourceKey: e,
          destinationKey: t,
          destinationBucket: s == null ? void 0 : s.destinationBucket
        }, { headers: this.headers })).Key }, error: null };
      } catch (n) {
        if (oe(n))
          return { data: null, error: n };
        throw n;
      }
    });
  }
  /**
   * Creates a signed URL. Use a signed URL to share a file for a fixed amount of time.
   *
   * @param path The file path, including the current file name. For example `folder/image.png`.
   * @param expiresIn The number of seconds until the signed URL expires. For example, `60` for a URL which is valid for one minute.
   * @param options.download triggers the file as a download if set to true. Set this parameter as the name of the file if you want to trigger the download with a different filename.
   * @param options.transform Transform the asset before serving it to the client.
   */
  createSignedUrl(e, t, s) {
    return ue(this, void 0, void 0, function* () {
      try {
        let n = this._getFinalPath(e), i = yield Re(this.fetch, `${this.url}/object/sign/${n}`, Object.assign({ expiresIn: t }, s != null && s.transform ? { transform: s.transform } : {}), { headers: this.headers });
        const a = s != null && s.download ? `&download=${s.download === !0 ? "" : s.download}` : "";
        return i = { signedUrl: encodeURI(`${this.url}${i.signedURL}${a}`) }, { data: i, error: null };
      } catch (n) {
        if (oe(n))
          return { data: null, error: n };
        throw n;
      }
    });
  }
  /**
   * Creates multiple signed URLs. Use a signed URL to share a file for a fixed amount of time.
   *
   * @param paths The file paths to be downloaded, including the current file names. For example `['folder/image.png', 'folder2/image2.png']`.
   * @param expiresIn The number of seconds until the signed URLs expire. For example, `60` for URLs which are valid for one minute.
   * @param options.download triggers the file as a download if set to true. Set this parameter as the name of the file if you want to trigger the download with a different filename.
   */
  createSignedUrls(e, t, s) {
    return ue(this, void 0, void 0, function* () {
      try {
        const n = yield Re(this.fetch, `${this.url}/object/sign/${this.bucketId}`, { expiresIn: t, paths: e }, { headers: this.headers }), i = s != null && s.download ? `&download=${s.download === !0 ? "" : s.download}` : "";
        return {
          data: n.map((a) => Object.assign(Object.assign({}, a), { signedUrl: a.signedURL ? encodeURI(`${this.url}${a.signedURL}${i}`) : null })),
          error: null
        };
      } catch (n) {
        if (oe(n))
          return { data: null, error: n };
        throw n;
      }
    });
  }
  /**
   * Downloads a file from a private bucket. For public buckets, make a request to the URL returned from `getPublicUrl` instead.
   *
   * @param path The full path and file name of the file to be downloaded. For example `folder/image.png`.
   * @param options.transform Transform the asset before serving it to the client.
   */
  download(e, t) {
    return ue(this, void 0, void 0, function* () {
      const n = typeof (t == null ? void 0 : t.transform) < "u" ? "render/image/authenticated" : "object", i = this.transformOptsToQueryString((t == null ? void 0 : t.transform) || {}), a = i ? `?${i}` : "";
      try {
        const l = this._getFinalPath(e);
        return { data: yield (yield Tt(this.fetch, `${this.url}/${n}/${l}${a}`, {
          headers: this.headers,
          noResolveJson: !0
        })).blob(), error: null };
      } catch (l) {
        if (oe(l))
          return { data: null, error: l };
        throw l;
      }
    });
  }
  /**
   * Retrieves the details of an existing file.
   * @param path
   */
  info(e) {
    return ue(this, void 0, void 0, function* () {
      const t = this._getFinalPath(e);
      try {
        const s = yield Tt(this.fetch, `${this.url}/object/info/${t}`, {
          headers: this.headers
        });
        return { data: Zt(s), error: null };
      } catch (s) {
        if (oe(s))
          return { data: null, error: s };
        throw s;
      }
    });
  }
  /**
   * Checks the existence of a file.
   * @param path
   */
  exists(e) {
    return ue(this, void 0, void 0, function* () {
      const t = this._getFinalPath(e);
      try {
        return yield Wi(this.fetch, `${this.url}/object/${t}`, {
          headers: this.headers
        }), { data: !0, error: null };
      } catch (s) {
        if (oe(s) && s instanceof Qt) {
          const n = s.originalError;
          if ([400, 404].includes(n == null ? void 0 : n.status))
            return { data: !1, error: s };
        }
        throw s;
      }
    });
  }
  /**
   * A simple convenience function to get the URL for an asset in a public bucket. If you do not want to use this function, you can construct the public URL by concatenating the bucket URL with the path to the asset.
   * This function does not verify if the bucket is public. If a public URL is created for a bucket which is not public, you will not be able to download the asset.
   *
   * @param path The path and name of the file to generate the public URL for. For example `folder/image.png`.
   * @param options.download Triggers the file as a download if set to true. Set this parameter as the name of the file if you want to trigger the download with a different filename.
   * @param options.transform Transform the asset before serving it to the client.
   */
  getPublicUrl(e, t) {
    const s = this._getFinalPath(e), n = [], i = t != null && t.download ? `download=${t.download === !0 ? "" : t.download}` : "";
    i !== "" && n.push(i);
    const l = typeof (t == null ? void 0 : t.transform) < "u" ? "render/image" : "object", o = this.transformOptsToQueryString((t == null ? void 0 : t.transform) || {});
    o !== "" && n.push(o);
    let c = n.join("&");
    return c !== "" && (c = `?${c}`), {
      data: { publicUrl: encodeURI(`${this.url}/${l}/public/${s}${c}`) }
    };
  }
  /**
   * Deletes files within the same bucket
   *
   * @param paths An array of files to delete, including the path and file name. For example [`'folder/image.png'`].
   */
  remove(e) {
    return ue(this, void 0, void 0, function* () {
      try {
        return { data: yield Lr(this.fetch, `${this.url}/object/${this.bucketId}`, { prefixes: e }, { headers: this.headers }), error: null };
      } catch (t) {
        if (oe(t))
          return { data: null, error: t };
        throw t;
      }
    });
  }
  /**
   * Get file metadata
   * @param id the file id to retrieve metadata
   */
  // async getMetadata(
  //   id: string
  // ): Promise<
  //   | {
  //       data: Metadata
  //       error: null
  //     }
  //   | {
  //       data: null
  //       error: StorageError
  //     }
  // > {
  //   try {
  //     const data = await get(this.fetch, `${this.url}/metadata/${id}`, { headers: this.headers })
  //     return { data, error: null }
  //   } catch (error) {
  //     if (isStorageError(error)) {
  //       return { data: null, error }
  //     }
  //     throw error
  //   }
  // }
  /**
   * Update file metadata
   * @param id the file id to update metadata
   * @param meta the new file metadata
   */
  // async updateMetadata(
  //   id: string,
  //   meta: Metadata
  // ): Promise<
  //   | {
  //       data: Metadata
  //       error: null
  //     }
  //   | {
  //       data: null
  //       error: StorageError
  //     }
  // > {
  //   try {
  //     const data = await post(
  //       this.fetch,
  //       `${this.url}/metadata/${id}`,
  //       { ...meta },
  //       { headers: this.headers }
  //     )
  //     return { data, error: null }
  //   } catch (error) {
  //     if (isStorageError(error)) {
  //       return { data: null, error }
  //     }
  //     throw error
  //   }
  // }
  /**
   * Lists all the files within a bucket.
   * @param path The folder path.
   */
  list(e, t, s) {
    return ue(this, void 0, void 0, function* () {
      try {
        const n = Object.assign(Object.assign(Object.assign({}, ji), t), { prefix: e || "" });
        return { data: yield Re(this.fetch, `${this.url}/object/list/${this.bucketId}`, n, { headers: this.headers }, s), error: null };
      } catch (n) {
        if (oe(n))
          return { data: null, error: n };
        throw n;
      }
    });
  }
  encodeMetadata(e) {
    return JSON.stringify(e);
  }
  toBase64(e) {
    return typeof Buffer < "u" ? Buffer.from(e).toString("base64") : btoa(e);
  }
  _getFinalPath(e) {
    return `${this.bucketId}/${e}`;
  }
  _removeEmptyFolders(e) {
    return e.replace(/^\/|\/$/g, "").replace(/\/+/g, "/");
  }
  transformOptsToQueryString(e) {
    const t = [];
    return e.width && t.push(`width=${e.width}`), e.height && t.push(`height=${e.height}`), e.resize && t.push(`resize=${e.resize}`), e.format && t.push(`format=${e.format}`), e.quality && t.push(`quality=${e.quality}`), t.join("&");
  }
}
const Fi = "2.7.1", Mi = { "X-Client-Info": `storage-js/${Fi}` };
var Je = function(r, e, t, s) {
  function n(i) {
    return i instanceof t ? i : new t(function(a) {
      a(i);
    });
  }
  return new (t || (t = Promise))(function(i, a) {
    function l(u) {
      try {
        c(s.next(u));
      } catch (h) {
        a(h);
      }
    }
    function o(u) {
      try {
        c(s.throw(u));
      } catch (h) {
        a(h);
      }
    }
    function c(u) {
      u.done ? i(u.value) : n(u.value).then(l, o);
    }
    c((s = s.apply(r, e || [])).next());
  });
};
class Hi {
  constructor(e, t = {}, s) {
    this.url = e, this.headers = Object.assign(Object.assign({}, Mi), t), this.fetch = Pr(s);
  }
  /**
   * Retrieves the details of all Storage buckets within an existing project.
   */
  listBuckets() {
    return Je(this, void 0, void 0, function* () {
      try {
        return { data: yield Tt(this.fetch, `${this.url}/bucket`, { headers: this.headers }), error: null };
      } catch (e) {
        if (oe(e))
          return { data: null, error: e };
        throw e;
      }
    });
  }
  /**
   * Retrieves the details of an existing Storage bucket.
   *
   * @param id The unique identifier of the bucket you would like to retrieve.
   */
  getBucket(e) {
    return Je(this, void 0, void 0, function* () {
      try {
        return { data: yield Tt(this.fetch, `${this.url}/bucket/${e}`, { headers: this.headers }), error: null };
      } catch (t) {
        if (oe(t))
          return { data: null, error: t };
        throw t;
      }
    });
  }
  /**
   * Creates a new Storage bucket
   *
   * @param id A unique identifier for the bucket you are creating.
   * @param options.public The visibility of the bucket. Public buckets don't require an authorization token to download objects, but still require a valid token for all other operations. By default, buckets are private.
   * @param options.fileSizeLimit specifies the max file size in bytes that can be uploaded to this bucket.
   * The global file size limit takes precedence over this value.
   * The default value is null, which doesn't set a per bucket file size limit.
   * @param options.allowedMimeTypes specifies the allowed mime types that this bucket can accept during upload.
   * The default value is null, which allows files with all mime types to be uploaded.
   * Each mime type specified can be a wildcard, e.g. image/*, or a specific mime type, e.g. image/png.
   * @returns newly created bucket id
   */
  createBucket(e, t = {
    public: !1
  }) {
    return Je(this, void 0, void 0, function* () {
      try {
        return { data: yield Re(this.fetch, `${this.url}/bucket`, {
          id: e,
          name: e,
          public: t.public,
          file_size_limit: t.fileSizeLimit,
          allowed_mime_types: t.allowedMimeTypes
        }, { headers: this.headers }), error: null };
      } catch (s) {
        if (oe(s))
          return { data: null, error: s };
        throw s;
      }
    });
  }
  /**
   * Updates a Storage bucket
   *
   * @param id A unique identifier for the bucket you are updating.
   * @param options.public The visibility of the bucket. Public buckets don't require an authorization token to download objects, but still require a valid token for all other operations.
   * @param options.fileSizeLimit specifies the max file size in bytes that can be uploaded to this bucket.
   * The global file size limit takes precedence over this value.
   * The default value is null, which doesn't set a per bucket file size limit.
   * @param options.allowedMimeTypes specifies the allowed mime types that this bucket can accept during upload.
   * The default value is null, which allows files with all mime types to be uploaded.
   * Each mime type specified can be a wildcard, e.g. image/*, or a specific mime type, e.g. image/png.
   */
  updateBucket(e, t) {
    return Je(this, void 0, void 0, function* () {
      try {
        return { data: yield Vi(this.fetch, `${this.url}/bucket/${e}`, {
          id: e,
          name: e,
          public: t.public,
          file_size_limit: t.fileSizeLimit,
          allowed_mime_types: t.allowedMimeTypes
        }, { headers: this.headers }), error: null };
      } catch (s) {
        if (oe(s))
          return { data: null, error: s };
        throw s;
      }
    });
  }
  /**
   * Removes all objects inside a single bucket.
   *
   * @param id The unique identifier of the bucket you would like to empty.
   */
  emptyBucket(e) {
    return Je(this, void 0, void 0, function* () {
      try {
        return { data: yield Re(this.fetch, `${this.url}/bucket/${e}/empty`, {}, { headers: this.headers }), error: null };
      } catch (t) {
        if (oe(t))
          return { data: null, error: t };
        throw t;
      }
    });
  }
  /**
   * Deletes an existing bucket. A bucket can't be deleted with existing objects inside it.
   * You must first `empty()` the bucket.
   *
   * @param id The unique identifier of the bucket you would like to delete.
   */
  deleteBucket(e) {
    return Je(this, void 0, void 0, function* () {
      try {
        return { data: yield Lr(this.fetch, `${this.url}/bucket/${e}`, {}, { headers: this.headers }), error: null };
      } catch (t) {
        if (oe(t))
          return { data: null, error: t };
        throw t;
      }
    });
  }
}
class $i extends Hi {
  constructor(e, t = {}, s) {
    super(e, t, s);
  }
  /**
   * Perform file operation in a bucket.
   *
   * @param id The bucket id to operate on.
   */
  from(e) {
    return new Ni(this.url, this.headers, e, this.fetch);
  }
}
const Bi = "2.49.1";
let ut = "";
typeof Deno < "u" ? ut = "deno" : typeof document < "u" ? ut = "web" : typeof navigator < "u" && navigator.product === "ReactNative" ? ut = "react-native" : ut = "node";
const Gi = { "X-Client-Info": `supabase-js-${ut}/${Bi}` }, qi = {
  headers: Gi
}, zi = {
  schema: "public"
}, xi = {
  autoRefreshToken: !0,
  persistSession: !0,
  detectSessionInUrl: !0,
  flowType: "implicit"
}, Ji = {};
var Ki = function(r, e, t, s) {
  function n(i) {
    return i instanceof t ? i : new t(function(a) {
      a(i);
    });
  }
  return new (t || (t = Promise))(function(i, a) {
    function l(u) {
      try {
        c(s.next(u));
      } catch (h) {
        a(h);
      }
    }
    function o(u) {
      try {
        c(s.throw(u));
      } catch (h) {
        a(h);
      }
    }
    function c(u) {
      u.done ? i(u.value) : n(u.value).then(l, o);
    }
    c((s = s.apply(r, e || [])).next());
  });
};
const Yi = (r) => {
  let e;
  return r ? e = r : typeof fetch > "u" ? e = pr : e = fetch, (...t) => e(...t);
}, Xi = () => typeof Headers > "u" ? Er : Headers, Qi = (r, e, t) => {
  const s = Yi(t), n = Xi();
  return (i, a) => Ki(void 0, void 0, void 0, function* () {
    var l;
    const o = (l = yield e()) !== null && l !== void 0 ? l : r;
    let c = new n(a == null ? void 0 : a.headers);
    return c.has("apikey") || c.set("apikey", r), c.has("Authorization") || c.set("Authorization", `Bearer ${o}`), s(i, Object.assign(Object.assign({}, a), { headers: c }));
  });
};
var Zi = function(r, e, t, s) {
  function n(i) {
    return i instanceof t ? i : new t(function(a) {
      a(i);
    });
  }
  return new (t || (t = Promise))(function(i, a) {
    function l(u) {
      try {
        c(s.next(u));
      } catch (h) {
        a(h);
      }
    }
    function o(u) {
      try {
        c(s.throw(u));
      } catch (h) {
        a(h);
      }
    }
    function c(u) {
      u.done ? i(u.value) : n(u.value).then(l, o);
    }
    c((s = s.apply(r, e || [])).next());
  });
};
function ea(r) {
  return r.replace(/\/$/, "");
}
function ta(r, e) {
  const { db: t, auth: s, realtime: n, global: i } = r, { db: a, auth: l, realtime: o, global: c } = e, u = {
    db: Object.assign(Object.assign({}, a), t),
    auth: Object.assign(Object.assign({}, l), s),
    realtime: Object.assign(Object.assign({}, o), n),
    global: Object.assign(Object.assign({}, c), i),
    accessToken: () => Zi(this, void 0, void 0, function* () {
      return "";
    })
  };
  return r.accessToken ? u.accessToken = r.accessToken : delete u.accessToken, u;
}
const Dr = "2.68.0", Qe = 30 * 1e3, es = 3, $t = es * Qe, sa = "http://localhost:9999", ra = "supabase.auth.token", na = { "X-Client-Info": `gotrue-js/${Dr}` }, ts = "X-Supabase-Api-Version", Ur = {
  "2024-01-01": {
    timestamp: Date.parse("2024-01-01T00:00:00.0Z"),
    name: "2024-01-01"
  }
};
function ia(r) {
  return Math.round(Date.now() / 1e3) + r;
}
function aa() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(r) {
    const e = Math.random() * 16 | 0;
    return (r == "x" ? e : e & 3 | 8).toString(16);
  });
}
const Se = () => typeof window < "u" && typeof document < "u", We = {
  tested: !1,
  writable: !1
}, ft = () => {
  if (!Se())
    return !1;
  try {
    if (typeof globalThis.localStorage != "object")
      return !1;
  } catch {
    return !1;
  }
  if (We.tested)
    return We.writable;
  const r = `lswt-${Math.random()}${Math.random()}`;
  try {
    globalThis.localStorage.setItem(r, r), globalThis.localStorage.removeItem(r), We.tested = !0, We.writable = !0;
  } catch {
    We.tested = !0, We.writable = !1;
  }
  return We.writable;
};
function oa(r) {
  const e = {}, t = new URL(r);
  if (t.hash && t.hash[0] === "#")
    try {
      new URLSearchParams(t.hash.substring(1)).forEach((n, i) => {
        e[i] = n;
      });
    } catch {
    }
  return t.searchParams.forEach((s, n) => {
    e[n] = s;
  }), e;
}
const Vr = (r) => {
  let e;
  return r ? e = r : typeof fetch > "u" ? e = (...t) => Promise.resolve().then(() => at).then(({ default: s }) => s(...t)) : e = fetch, (...t) => e(...t);
}, la = (r) => typeof r == "object" && r !== null && "status" in r && "ok" in r && "json" in r && typeof r.json == "function", Wr = async (r, e, t) => {
  await r.setItem(e, JSON.stringify(t));
}, wt = async (r, e) => {
  const t = await r.getItem(e);
  if (!t)
    return null;
  try {
    return JSON.parse(t);
  } catch {
    return t;
  }
}, St = async (r, e) => {
  await r.removeItem(e);
};
function ca(r) {
  const e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
  let t = "", s, n, i, a, l, o, c, u = 0;
  for (r = r.replace("-", "+").replace("_", "/"); u < r.length; )
    a = e.indexOf(r.charAt(u++)), l = e.indexOf(r.charAt(u++)), o = e.indexOf(r.charAt(u++)), c = e.indexOf(r.charAt(u++)), s = a << 2 | l >> 4, n = (l & 15) << 4 | o >> 2, i = (o & 3) << 6 | c, t = t + String.fromCharCode(s), o != 64 && n != 0 && (t = t + String.fromCharCode(n)), c != 64 && i != 0 && (t = t + String.fromCharCode(i));
  return t;
}
class Nt {
  constructor() {
    this.promise = new Nt.promiseConstructor((e, t) => {
      this.resolve = e, this.reject = t;
    });
  }
}
Nt.promiseConstructor = Promise;
function zs(r) {
  const e = /^([a-z0-9_-]{4})*($|[a-z0-9_-]{3}=?$|[a-z0-9_-]{2}(==)?$)$/i, t = r.split(".");
  if (t.length !== 3)
    throw new Error("JWT is not valid: not a JWT structure");
  if (!e.test(t[1]))
    throw new Error("JWT is not valid: payload is not in base64url format");
  const s = t[1];
  return JSON.parse(ca(s));
}
async function ua(r) {
  return await new Promise((e) => {
    setTimeout(() => e(null), r);
  });
}
function ha(r, e) {
  return new Promise((s, n) => {
    (async () => {
      for (let i = 0; i < 1 / 0; i++)
        try {
          const a = await r(i);
          if (!e(i, null, a)) {
            s(a);
            return;
          }
        } catch (a) {
          if (!e(i, a)) {
            n(a);
            return;
          }
        }
    })();
  });
}
function da(r) {
  return ("0" + r.toString(16)).substr(-2);
}
function fa() {
  const e = new Uint32Array(56);
  if (typeof crypto > "u") {
    const t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~", s = t.length;
    let n = "";
    for (let i = 0; i < 56; i++)
      n += t.charAt(Math.floor(Math.random() * s));
    return n;
  }
  return crypto.getRandomValues(e), Array.from(e, da).join("");
}
async function _a(r) {
  const t = new TextEncoder().encode(r), s = await crypto.subtle.digest("SHA-256", t), n = new Uint8Array(s);
  return Array.from(n).map((i) => String.fromCharCode(i)).join("");
}
function ga(r) {
  return btoa(r).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
async function pa(r) {
  if (!(typeof crypto < "u" && typeof crypto.subtle < "u" && typeof TextEncoder < "u"))
    return console.warn("WebCrypto API is not supported. Code challenge method will default to use plain instead of sha256."), r;
  const t = await _a(r);
  return ga(t);
}
async function Ke(r, e, t = !1) {
  const s = fa();
  let n = s;
  t && (n += "/PASSWORD_RECOVERY"), await Wr(r, `${e}-code-verifier`, n);
  const i = await pa(s);
  return [i, s === i ? "plain" : "s256"];
}
const Ea = /^2[0-9]{3}-(0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-9]|3[0-1])$/i;
function va(r) {
  const e = r.headers.get(ts);
  if (!e || !e.match(Ea))
    return null;
  try {
    return /* @__PURE__ */ new Date(`${e}T00:00:00.0Z`);
  } catch {
    return null;
  }
}
class us extends Error {
  constructor(e, t, s) {
    super(e), this.__isAuthError = !0, this.name = "AuthError", this.status = t, this.code = s;
  }
}
function N(r) {
  return typeof r == "object" && r !== null && "__isAuthError" in r;
}
class ma extends us {
  constructor(e, t, s) {
    super(e, t, s), this.name = "AuthApiError", this.status = t, this.code = s;
  }
}
function ba(r) {
  return N(r) && r.name === "AuthApiError";
}
class jr extends us {
  constructor(e, t) {
    super(e), this.name = "AuthUnknownError", this.originalError = t;
  }
}
class He extends us {
  constructor(e, t, s, n) {
    super(e, s, n), this.name = t, this.status = s;
  }
}
class Ce extends He {
  constructor() {
    super("Auth session missing!", "AuthSessionMissingError", 400, void 0);
  }
}
function ya(r) {
  return N(r) && r.name === "AuthSessionMissingError";
}
class Bt extends He {
  constructor() {
    super("Auth session or user missing", "AuthInvalidTokenResponseError", 500, void 0);
  }
}
class It extends He {
  constructor(e) {
    super(e, "AuthInvalidCredentialsError", 400, void 0);
  }
}
class At extends He {
  constructor(e, t = null) {
    super(e, "AuthImplicitGrantRedirectError", 500, void 0), this.details = null, this.details = t;
  }
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      status: this.status,
      details: this.details
    };
  }
}
function wa(r) {
  return N(r) && r.name === "AuthImplicitGrantRedirectError";
}
class xs extends He {
  constructor(e, t = null) {
    super(e, "AuthPKCEGrantCodeExchangeError", 500, void 0), this.details = null, this.details = t;
  }
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      status: this.status,
      details: this.details
    };
  }
}
class ss extends He {
  constructor(e, t) {
    super(e, "AuthRetryableFetchError", t, void 0);
  }
}
function Gt(r) {
  return N(r) && r.name === "AuthRetryableFetchError";
}
class Js extends He {
  constructor(e, t, s) {
    super(e, "AuthWeakPasswordError", t, "weak_password"), this.reasons = s;
  }
}
var Sa = function(r, e) {
  var t = {};
  for (var s in r) Object.prototype.hasOwnProperty.call(r, s) && e.indexOf(s) < 0 && (t[s] = r[s]);
  if (r != null && typeof Object.getOwnPropertySymbols == "function")
    for (var n = 0, s = Object.getOwnPropertySymbols(r); n < s.length; n++)
      e.indexOf(s[n]) < 0 && Object.prototype.propertyIsEnumerable.call(r, s[n]) && (t[s[n]] = r[s[n]]);
  return t;
};
const je = (r) => r.msg || r.message || r.error_description || r.error || JSON.stringify(r), Ia = [502, 503, 504];
async function Ks(r) {
  var e;
  if (!la(r))
    throw new ss(je(r), 0);
  if (Ia.includes(r.status))
    throw new ss(je(r), r.status);
  let t;
  try {
    t = await r.json();
  } catch (i) {
    throw new jr(je(i), i);
  }
  let s;
  const n = va(r);
  if (n && n.getTime() >= Ur["2024-01-01"].timestamp && typeof t == "object" && t && typeof t.code == "string" ? s = t.code : typeof t == "object" && t && typeof t.error_code == "string" && (s = t.error_code), s) {
    if (s === "weak_password")
      throw new Js(je(t), r.status, ((e = t.weak_password) === null || e === void 0 ? void 0 : e.reasons) || []);
    if (s === "session_not_found")
      throw new Ce();
  } else if (typeof t == "object" && t && typeof t.weak_password == "object" && t.weak_password && Array.isArray(t.weak_password.reasons) && t.weak_password.reasons.length && t.weak_password.reasons.reduce((i, a) => i && typeof a == "string", !0))
    throw new Js(je(t), r.status, t.weak_password.reasons);
  throw new ma(je(t), r.status || 500, s);
}
const Aa = (r, e, t, s) => {
  const n = { method: r, headers: (e == null ? void 0 : e.headers) || {} };
  return r === "GET" ? n : (n.headers = Object.assign({ "Content-Type": "application/json;charset=UTF-8" }, e == null ? void 0 : e.headers), n.body = JSON.stringify(s), Object.assign(Object.assign({}, n), t));
};
async function G(r, e, t, s) {
  var n;
  const i = Object.assign({}, s == null ? void 0 : s.headers);
  i[ts] || (i[ts] = Ur["2024-01-01"].name), s != null && s.jwt && (i.Authorization = `Bearer ${s.jwt}`);
  const a = (n = s == null ? void 0 : s.query) !== null && n !== void 0 ? n : {};
  s != null && s.redirectTo && (a.redirect_to = s.redirectTo);
  const l = Object.keys(a).length ? "?" + new URLSearchParams(a).toString() : "", o = await Oa(r, e, t + l, {
    headers: i,
    noResolveJson: s == null ? void 0 : s.noResolveJson
  }, {}, s == null ? void 0 : s.body);
  return s != null && s.xform ? s == null ? void 0 : s.xform(o) : { data: Object.assign({}, o), error: null };
}
async function Oa(r, e, t, s, n, i) {
  const a = Aa(e, s, n, i);
  let l;
  try {
    l = await r(t, Object.assign({}, a));
  } catch (o) {
    throw console.error(o), new ss(je(o), 0);
  }
  if (l.ok || await Ks(l), s != null && s.noResolveJson)
    return l;
  try {
    return await l.json();
  } catch (o) {
    await Ks(o);
  }
}
function Te(r) {
  var e;
  let t = null;
  ka(r) && (t = Object.assign({}, r), r.expires_at || (t.expires_at = ia(r.expires_in)));
  const s = (e = r.user) !== null && e !== void 0 ? e : r;
  return { data: { session: t, user: s }, error: null };
}
function Ys(r) {
  const e = Te(r);
  return !e.error && r.weak_password && typeof r.weak_password == "object" && Array.isArray(r.weak_password.reasons) && r.weak_password.reasons.length && r.weak_password.message && typeof r.weak_password.message == "string" && r.weak_password.reasons.reduce((t, s) => t && typeof s == "string", !0) && (e.data.weak_password = r.weak_password), e;
}
function ke(r) {
  var e;
  return { data: { user: (e = r.user) !== null && e !== void 0 ? e : r }, error: null };
}
function Ca(r) {
  return { data: r, error: null };
}
function Ta(r) {
  const { action_link: e, email_otp: t, hashed_token: s, redirect_to: n, verification_type: i } = r, a = Sa(r, ["action_link", "email_otp", "hashed_token", "redirect_to", "verification_type"]), l = {
    action_link: e,
    email_otp: t,
    hashed_token: s,
    redirect_to: n,
    verification_type: i
  }, o = Object.assign({}, a);
  return {
    data: {
      properties: l,
      user: o
    },
    error: null
  };
}
function Ra(r) {
  return r;
}
function ka(r) {
  return r.access_token && r.refresh_token && r.expires_in;
}
var Pa = function(r, e) {
  var t = {};
  for (var s in r) Object.prototype.hasOwnProperty.call(r, s) && e.indexOf(s) < 0 && (t[s] = r[s]);
  if (r != null && typeof Object.getOwnPropertySymbols == "function")
    for (var n = 0, s = Object.getOwnPropertySymbols(r); n < s.length; n++)
      e.indexOf(s[n]) < 0 && Object.prototype.propertyIsEnumerable.call(r, s[n]) && (t[s[n]] = r[s[n]]);
  return t;
};
class La {
  constructor({ url: e = "", headers: t = {}, fetch: s }) {
    this.url = e, this.headers = t, this.fetch = Vr(s), this.mfa = {
      listFactors: this._listFactors.bind(this),
      deleteFactor: this._deleteFactor.bind(this)
    };
  }
  /**
   * Removes a logged-in session.
   * @param jwt A valid, logged-in JWT.
   * @param scope The logout sope.
   */
  async signOut(e, t = "global") {
    try {
      return await G(this.fetch, "POST", `${this.url}/logout?scope=${t}`, {
        headers: this.headers,
        jwt: e,
        noResolveJson: !0
      }), { data: null, error: null };
    } catch (s) {
      if (N(s))
        return { data: null, error: s };
      throw s;
    }
  }
  /**
   * Sends an invite link to an email address.
   * @param email The email address of the user.
   * @param options Additional options to be included when inviting.
   */
  async inviteUserByEmail(e, t = {}) {
    try {
      return await G(this.fetch, "POST", `${this.url}/invite`, {
        body: { email: e, data: t.data },
        headers: this.headers,
        redirectTo: t.redirectTo,
        xform: ke
      });
    } catch (s) {
      if (N(s))
        return { data: { user: null }, error: s };
      throw s;
    }
  }
  /**
   * Generates email links and OTPs to be sent via a custom email provider.
   * @param email The user's email.
   * @param options.password User password. For signup only.
   * @param options.data Optional user metadata. For signup only.
   * @param options.redirectTo The redirect url which should be appended to the generated link
   */
  async generateLink(e) {
    try {
      const { options: t } = e, s = Pa(e, ["options"]), n = Object.assign(Object.assign({}, s), t);
      return "newEmail" in s && (n.new_email = s == null ? void 0 : s.newEmail, delete n.newEmail), await G(this.fetch, "POST", `${this.url}/admin/generate_link`, {
        body: n,
        headers: this.headers,
        xform: Ta,
        redirectTo: t == null ? void 0 : t.redirectTo
      });
    } catch (t) {
      if (N(t))
        return {
          data: {
            properties: null,
            user: null
          },
          error: t
        };
      throw t;
    }
  }
  // User Admin API
  /**
   * Creates a new user.
   * This function should only be called on a server. Never expose your `service_role` key in the browser.
   */
  async createUser(e) {
    try {
      return await G(this.fetch, "POST", `${this.url}/admin/users`, {
        body: e,
        headers: this.headers,
        xform: ke
      });
    } catch (t) {
      if (N(t))
        return { data: { user: null }, error: t };
      throw t;
    }
  }
  /**
   * Get a list of users.
   *
   * This function should only be called on a server. Never expose your `service_role` key in the browser.
   * @param params An object which supports `page` and `perPage` as numbers, to alter the paginated results.
   */
  async listUsers(e) {
    var t, s, n, i, a, l, o;
    try {
      const c = { nextPage: null, lastPage: 0, total: 0 }, u = await G(this.fetch, "GET", `${this.url}/admin/users`, {
        headers: this.headers,
        noResolveJson: !0,
        query: {
          page: (s = (t = e == null ? void 0 : e.page) === null || t === void 0 ? void 0 : t.toString()) !== null && s !== void 0 ? s : "",
          per_page: (i = (n = e == null ? void 0 : e.perPage) === null || n === void 0 ? void 0 : n.toString()) !== null && i !== void 0 ? i : ""
        },
        xform: Ra
      });
      if (u.error)
        throw u.error;
      const h = await u.json(), d = (a = u.headers.get("x-total-count")) !== null && a !== void 0 ? a : 0, _ = (o = (l = u.headers.get("link")) === null || l === void 0 ? void 0 : l.split(",")) !== null && o !== void 0 ? o : [];
      return _.length > 0 && (_.forEach((p) => {
        const v = parseInt(p.split(";")[0].split("=")[1].substring(0, 1)), w = JSON.parse(p.split(";")[1].split("=")[1]);
        c[`${w}Page`] = v;
      }), c.total = parseInt(d)), { data: Object.assign(Object.assign({}, h), c), error: null };
    } catch (c) {
      if (N(c))
        return { data: { users: [] }, error: c };
      throw c;
    }
  }
  /**
   * Get user by id.
   *
   * @param uid The user's unique identifier
   *
   * This function should only be called on a server. Never expose your `service_role` key in the browser.
   */
  async getUserById(e) {
    try {
      return await G(this.fetch, "GET", `${this.url}/admin/users/${e}`, {
        headers: this.headers,
        xform: ke
      });
    } catch (t) {
      if (N(t))
        return { data: { user: null }, error: t };
      throw t;
    }
  }
  /**
   * Updates the user data.
   *
   * @param attributes The data you want to update.
   *
   * This function should only be called on a server. Never expose your `service_role` key in the browser.
   */
  async updateUserById(e, t) {
    try {
      return await G(this.fetch, "PUT", `${this.url}/admin/users/${e}`, {
        body: t,
        headers: this.headers,
        xform: ke
      });
    } catch (s) {
      if (N(s))
        return { data: { user: null }, error: s };
      throw s;
    }
  }
  /**
   * Delete a user. Requires a `service_role` key.
   *
   * @param id The user id you want to remove.
   * @param shouldSoftDelete If true, then the user will be soft-deleted from the auth schema. Soft deletion allows user identification from the hashed user ID but is not reversible.
   * Defaults to false for backward compatibility.
   *
   * This function should only be called on a server. Never expose your `service_role` key in the browser.
   */
  async deleteUser(e, t = !1) {
    try {
      return await G(this.fetch, "DELETE", `${this.url}/admin/users/${e}`, {
        headers: this.headers,
        body: {
          should_soft_delete: t
        },
        xform: ke
      });
    } catch (s) {
      if (N(s))
        return { data: { user: null }, error: s };
      throw s;
    }
  }
  async _listFactors(e) {
    try {
      const { data: t, error: s } = await G(this.fetch, "GET", `${this.url}/admin/users/${e.userId}/factors`, {
        headers: this.headers,
        xform: (n) => ({ data: { factors: n }, error: null })
      });
      return { data: t, error: s };
    } catch (t) {
      if (N(t))
        return { data: null, error: t };
      throw t;
    }
  }
  async _deleteFactor(e) {
    try {
      return { data: await G(this.fetch, "DELETE", `${this.url}/admin/users/${e.userId}/factors/${e.id}`, {
        headers: this.headers
      }), error: null };
    } catch (t) {
      if (N(t))
        return { data: null, error: t };
      throw t;
    }
  }
}
const Da = {
  getItem: (r) => ft() ? globalThis.localStorage.getItem(r) : null,
  setItem: (r, e) => {
    ft() && globalThis.localStorage.setItem(r, e);
  },
  removeItem: (r) => {
    ft() && globalThis.localStorage.removeItem(r);
  }
};
function Xs(r = {}) {
  return {
    getItem: (e) => r[e] || null,
    setItem: (e, t) => {
      r[e] = t;
    },
    removeItem: (e) => {
      delete r[e];
    }
  };
}
function Ua() {
  if (typeof globalThis != "object")
    try {
      Object.defineProperty(Object.prototype, "__magic__", {
        get: function() {
          return this;
        },
        configurable: !0
      }), __magic__.globalThis = __magic__, delete Object.prototype.__magic__;
    } catch {
      typeof self < "u" && (self.globalThis = self);
    }
}
const Ye = {
  /**
   * @experimental
   */
  debug: !!(globalThis && ft() && globalThis.localStorage && globalThis.localStorage.getItem("supabase.gotrue-js.locks.debug") === "true")
};
class Nr extends Error {
  constructor(e) {
    super(e), this.isAcquireTimeout = !0;
  }
}
class Va extends Nr {
}
async function Wa(r, e, t) {
  Ye.debug && console.log("@supabase/gotrue-js: navigatorLock: acquire lock", r, e);
  const s = new globalThis.AbortController();
  return e > 0 && setTimeout(() => {
    s.abort(), Ye.debug && console.log("@supabase/gotrue-js: navigatorLock acquire timed out", r);
  }, e), await Promise.resolve().then(() => globalThis.navigator.locks.request(r, e === 0 ? {
    mode: "exclusive",
    ifAvailable: !0
  } : {
    mode: "exclusive",
    signal: s.signal
  }, async (n) => {
    if (n) {
      Ye.debug && console.log("@supabase/gotrue-js: navigatorLock: acquired", r, n.name);
      try {
        return await t();
      } finally {
        Ye.debug && console.log("@supabase/gotrue-js: navigatorLock: released", r, n.name);
      }
    } else {
      if (e === 0)
        throw Ye.debug && console.log("@supabase/gotrue-js: navigatorLock: not immediately available", r), new Va(`Acquiring an exclusive Navigator LockManager lock "${r}" immediately failed`);
      if (Ye.debug)
        try {
          const i = await globalThis.navigator.locks.query();
          console.log("@supabase/gotrue-js: Navigator LockManager state", JSON.stringify(i, null, "  "));
        } catch (i) {
          console.warn("@supabase/gotrue-js: Error when querying Navigator LockManager state", i);
        }
      return console.warn("@supabase/gotrue-js: Navigator LockManager returned a null lock when using #request without ifAvailable set to true, it appears this browser is not following the LockManager spec https://developer.mozilla.org/en-US/docs/Web/API/LockManager/request"), await t();
    }
  }));
}
Ua();
const ja = {
  url: sa,
  storageKey: ra,
  autoRefreshToken: !0,
  persistSession: !0,
  detectSessionInUrl: !0,
  headers: na,
  flowType: "implicit",
  debug: !1,
  hasCustomAuthorizationHeader: !1
};
async function Qs(r, e, t) {
  return await t();
}
class gt {
  /**
   * Create a new client for use in the browser.
   */
  constructor(e) {
    var t, s;
    this.memoryStorage = null, this.stateChangeEmitters = /* @__PURE__ */ new Map(), this.autoRefreshTicker = null, this.visibilityChangedCallback = null, this.refreshingDeferred = null, this.initializePromise = null, this.detectSessionInUrl = !0, this.hasCustomAuthorizationHeader = !1, this.suppressGetSessionWarning = !1, this.lockAcquired = !1, this.pendingInLock = [], this.broadcastChannel = null, this.logger = console.log, this.instanceID = gt.nextInstanceID, gt.nextInstanceID += 1, this.instanceID > 0 && Se() && console.warn("Multiple GoTrueClient instances detected in the same browser context. It is not an error, but this should be avoided as it may produce undefined behavior when used concurrently under the same storage key.");
    const n = Object.assign(Object.assign({}, ja), e);
    if (this.logDebugMessages = !!n.debug, typeof n.debug == "function" && (this.logger = n.debug), this.persistSession = n.persistSession, this.storageKey = n.storageKey, this.autoRefreshToken = n.autoRefreshToken, this.admin = new La({
      url: n.url,
      headers: n.headers,
      fetch: n.fetch
    }), this.url = n.url, this.headers = n.headers, this.fetch = Vr(n.fetch), this.lock = n.lock || Qs, this.detectSessionInUrl = n.detectSessionInUrl, this.flowType = n.flowType, this.hasCustomAuthorizationHeader = n.hasCustomAuthorizationHeader, n.lock ? this.lock = n.lock : Se() && (!((t = globalThis == null ? void 0 : globalThis.navigator) === null || t === void 0) && t.locks) ? this.lock = Wa : this.lock = Qs, this.mfa = {
      verify: this._verify.bind(this),
      enroll: this._enroll.bind(this),
      unenroll: this._unenroll.bind(this),
      challenge: this._challenge.bind(this),
      listFactors: this._listFactors.bind(this),
      challengeAndVerify: this._challengeAndVerify.bind(this),
      getAuthenticatorAssuranceLevel: this._getAuthenticatorAssuranceLevel.bind(this)
    }, this.persistSession ? n.storage ? this.storage = n.storage : ft() ? this.storage = Da : (this.memoryStorage = {}, this.storage = Xs(this.memoryStorage)) : (this.memoryStorage = {}, this.storage = Xs(this.memoryStorage)), Se() && globalThis.BroadcastChannel && this.persistSession && this.storageKey) {
      try {
        this.broadcastChannel = new globalThis.BroadcastChannel(this.storageKey);
      } catch (i) {
        console.error("Failed to create a new BroadcastChannel, multi-tab state changes will not be available", i);
      }
      (s = this.broadcastChannel) === null || s === void 0 || s.addEventListener("message", async (i) => {
        this._debug("received broadcast notification from other tab or client", i), await this._notifyAllSubscribers(i.data.event, i.data.session, !1);
      });
    }
    this.initialize();
  }
  _debug(...e) {
    return this.logDebugMessages && this.logger(`GoTrueClient@${this.instanceID} (${Dr}) ${(/* @__PURE__ */ new Date()).toISOString()}`, ...e), this;
  }
  /**
   * Initializes the client session either from the url or from storage.
   * This method is automatically called when instantiating the client, but should also be called
   * manually when checking for an error from an auth redirect (oauth, magiclink, password recovery, etc).
   */
  async initialize() {
    return this.initializePromise ? await this.initializePromise : (this.initializePromise = (async () => await this._acquireLock(-1, async () => await this._initialize()))(), await this.initializePromise);
  }
  /**
   * IMPORTANT:
   * 1. Never throw in this method, as it is called from the constructor
   * 2. Never return a session from this method as it would be cached over
   *    the whole lifetime of the client
   */
  async _initialize() {
    var e;
    try {
      const t = oa(window.location.href);
      let s = "none";
      if (this._isImplicitGrantCallback(t) ? s = "implicit" : await this._isPKCECallback(t) && (s = "pkce"), Se() && this.detectSessionInUrl && s !== "none") {
        const { data: n, error: i } = await this._getSessionFromURL(t, s);
        if (i) {
          if (this._debug("#_initialize()", "error detecting session from URL", i), wa(i)) {
            const o = (e = i.details) === null || e === void 0 ? void 0 : e.code;
            if (o === "identity_already_exists" || o === "identity_not_found" || o === "single_identity_not_deletable")
              return { error: i };
          }
          return await this._removeSession(), { error: i };
        }
        const { session: a, redirectType: l } = n;
        return this._debug("#_initialize()", "detected session in URL", a, "redirect type", l), await this._saveSession(a), setTimeout(async () => {
          l === "recovery" ? await this._notifyAllSubscribers("PASSWORD_RECOVERY", a) : await this._notifyAllSubscribers("SIGNED_IN", a);
        }, 0), { error: null };
      }
      return await this._recoverAndRefresh(), { error: null };
    } catch (t) {
      return N(t) ? { error: t } : {
        error: new jr("Unexpected error during initialization", t)
      };
    } finally {
      await this._handleVisibilityChange(), this._debug("#_initialize()", "end");
    }
  }
  /**
   * Creates a new anonymous user.
   *
   * @returns A session where the is_anonymous claim in the access token JWT set to true
   */
  async signInAnonymously(e) {
    var t, s, n;
    try {
      const i = await G(this.fetch, "POST", `${this.url}/signup`, {
        headers: this.headers,
        body: {
          data: (s = (t = e == null ? void 0 : e.options) === null || t === void 0 ? void 0 : t.data) !== null && s !== void 0 ? s : {},
          gotrue_meta_security: { captcha_token: (n = e == null ? void 0 : e.options) === null || n === void 0 ? void 0 : n.captchaToken }
        },
        xform: Te
      }), { data: a, error: l } = i;
      if (l || !a)
        return { data: { user: null, session: null }, error: l };
      const o = a.session, c = a.user;
      return a.session && (await this._saveSession(a.session), await this._notifyAllSubscribers("SIGNED_IN", o)), { data: { user: c, session: o }, error: null };
    } catch (i) {
      if (N(i))
        return { data: { user: null, session: null }, error: i };
      throw i;
    }
  }
  /**
   * Creates a new user.
   *
   * Be aware that if a user account exists in the system you may get back an
   * error message that attempts to hide this information from the user.
   * This method has support for PKCE via email signups. The PKCE flow cannot be used when autoconfirm is enabled.
   *
   * @returns A logged-in session if the server has "autoconfirm" ON
   * @returns A user if the server has "autoconfirm" OFF
   */
  async signUp(e) {
    var t, s, n;
    try {
      let i;
      if ("email" in e) {
        const { email: u, password: h, options: d } = e;
        let _ = null, p = null;
        this.flowType === "pkce" && ([_, p] = await Ke(this.storage, this.storageKey)), i = await G(this.fetch, "POST", `${this.url}/signup`, {
          headers: this.headers,
          redirectTo: d == null ? void 0 : d.emailRedirectTo,
          body: {
            email: u,
            password: h,
            data: (t = d == null ? void 0 : d.data) !== null && t !== void 0 ? t : {},
            gotrue_meta_security: { captcha_token: d == null ? void 0 : d.captchaToken },
            code_challenge: _,
            code_challenge_method: p
          },
          xform: Te
        });
      } else if ("phone" in e) {
        const { phone: u, password: h, options: d } = e;
        i = await G(this.fetch, "POST", `${this.url}/signup`, {
          headers: this.headers,
          body: {
            phone: u,
            password: h,
            data: (s = d == null ? void 0 : d.data) !== null && s !== void 0 ? s : {},
            channel: (n = d == null ? void 0 : d.channel) !== null && n !== void 0 ? n : "sms",
            gotrue_meta_security: { captcha_token: d == null ? void 0 : d.captchaToken }
          },
          xform: Te
        });
      } else
        throw new It("You must provide either an email or phone number and a password");
      const { data: a, error: l } = i;
      if (l || !a)
        return { data: { user: null, session: null }, error: l };
      const o = a.session, c = a.user;
      return a.session && (await this._saveSession(a.session), await this._notifyAllSubscribers("SIGNED_IN", o)), { data: { user: c, session: o }, error: null };
    } catch (i) {
      if (N(i))
        return { data: { user: null, session: null }, error: i };
      throw i;
    }
  }
  /**
   * Log in an existing user with an email and password or phone and password.
   *
   * Be aware that you may get back an error message that will not distinguish
   * between the cases where the account does not exist or that the
   * email/phone and password combination is wrong or that the account can only
   * be accessed via social login.
   */
  async signInWithPassword(e) {
    try {
      let t;
      if ("email" in e) {
        const { email: i, password: a, options: l } = e;
        t = await G(this.fetch, "POST", `${this.url}/token?grant_type=password`, {
          headers: this.headers,
          body: {
            email: i,
            password: a,
            gotrue_meta_security: { captcha_token: l == null ? void 0 : l.captchaToken }
          },
          xform: Ys
        });
      } else if ("phone" in e) {
        const { phone: i, password: a, options: l } = e;
        t = await G(this.fetch, "POST", `${this.url}/token?grant_type=password`, {
          headers: this.headers,
          body: {
            phone: i,
            password: a,
            gotrue_meta_security: { captcha_token: l == null ? void 0 : l.captchaToken }
          },
          xform: Ys
        });
      } else
        throw new It("You must provide either an email or phone number and a password");
      const { data: s, error: n } = t;
      return n ? { data: { user: null, session: null }, error: n } : !s || !s.session || !s.user ? { data: { user: null, session: null }, error: new Bt() } : (s.session && (await this._saveSession(s.session), await this._notifyAllSubscribers("SIGNED_IN", s.session)), {
        data: Object.assign({ user: s.user, session: s.session }, s.weak_password ? { weakPassword: s.weak_password } : null),
        error: n
      });
    } catch (t) {
      if (N(t))
        return { data: { user: null, session: null }, error: t };
      throw t;
    }
  }
  /**
   * Log in an existing user via a third-party provider.
   * This method supports the PKCE flow.
   */
  async signInWithOAuth(e) {
    var t, s, n, i;
    return await this._handleProviderSignIn(e.provider, {
      redirectTo: (t = e.options) === null || t === void 0 ? void 0 : t.redirectTo,
      scopes: (s = e.options) === null || s === void 0 ? void 0 : s.scopes,
      queryParams: (n = e.options) === null || n === void 0 ? void 0 : n.queryParams,
      skipBrowserRedirect: (i = e.options) === null || i === void 0 ? void 0 : i.skipBrowserRedirect
    });
  }
  /**
   * Log in an existing user by exchanging an Auth Code issued during the PKCE flow.
   */
  async exchangeCodeForSession(e) {
    return await this.initializePromise, this._acquireLock(-1, async () => this._exchangeCodeForSession(e));
  }
  async _exchangeCodeForSession(e) {
    const t = await wt(this.storage, `${this.storageKey}-code-verifier`), [s, n] = (t ?? "").split("/");
    try {
      const { data: i, error: a } = await G(this.fetch, "POST", `${this.url}/token?grant_type=pkce`, {
        headers: this.headers,
        body: {
          auth_code: e,
          code_verifier: s
        },
        xform: Te
      });
      if (await St(this.storage, `${this.storageKey}-code-verifier`), a)
        throw a;
      return !i || !i.session || !i.user ? {
        data: { user: null, session: null, redirectType: null },
        error: new Bt()
      } : (i.session && (await this._saveSession(i.session), await this._notifyAllSubscribers("SIGNED_IN", i.session)), { data: Object.assign(Object.assign({}, i), { redirectType: n ?? null }), error: a });
    } catch (i) {
      if (N(i))
        return { data: { user: null, session: null, redirectType: null }, error: i };
      throw i;
    }
  }
  /**
   * Allows signing in with an OIDC ID token. The authentication provider used
   * should be enabled and configured.
   */
  async signInWithIdToken(e) {
    try {
      const { options: t, provider: s, token: n, access_token: i, nonce: a } = e, l = await G(this.fetch, "POST", `${this.url}/token?grant_type=id_token`, {
        headers: this.headers,
        body: {
          provider: s,
          id_token: n,
          access_token: i,
          nonce: a,
          gotrue_meta_security: { captcha_token: t == null ? void 0 : t.captchaToken }
        },
        xform: Te
      }), { data: o, error: c } = l;
      return c ? { data: { user: null, session: null }, error: c } : !o || !o.session || !o.user ? {
        data: { user: null, session: null },
        error: new Bt()
      } : (o.session && (await this._saveSession(o.session), await this._notifyAllSubscribers("SIGNED_IN", o.session)), { data: o, error: c });
    } catch (t) {
      if (N(t))
        return { data: { user: null, session: null }, error: t };
      throw t;
    }
  }
  /**
   * Log in a user using magiclink or a one-time password (OTP).
   *
   * If the `{{ .ConfirmationURL }}` variable is specified in the email template, a magiclink will be sent.
   * If the `{{ .Token }}` variable is specified in the email template, an OTP will be sent.
   * If you're using phone sign-ins, only an OTP will be sent. You won't be able to send a magiclink for phone sign-ins.
   *
   * Be aware that you may get back an error message that will not distinguish
   * between the cases where the account does not exist or, that the account
   * can only be accessed via social login.
   *
   * Do note that you will need to configure a Whatsapp sender on Twilio
   * if you are using phone sign in with the 'whatsapp' channel. The whatsapp
   * channel is not supported on other providers
   * at this time.
   * This method supports PKCE when an email is passed.
   */
  async signInWithOtp(e) {
    var t, s, n, i, a;
    try {
      if ("email" in e) {
        const { email: l, options: o } = e;
        let c = null, u = null;
        this.flowType === "pkce" && ([c, u] = await Ke(this.storage, this.storageKey));
        const { error: h } = await G(this.fetch, "POST", `${this.url}/otp`, {
          headers: this.headers,
          body: {
            email: l,
            data: (t = o == null ? void 0 : o.data) !== null && t !== void 0 ? t : {},
            create_user: (s = o == null ? void 0 : o.shouldCreateUser) !== null && s !== void 0 ? s : !0,
            gotrue_meta_security: { captcha_token: o == null ? void 0 : o.captchaToken },
            code_challenge: c,
            code_challenge_method: u
          },
          redirectTo: o == null ? void 0 : o.emailRedirectTo
        });
        return { data: { user: null, session: null }, error: h };
      }
      if ("phone" in e) {
        const { phone: l, options: o } = e, { data: c, error: u } = await G(this.fetch, "POST", `${this.url}/otp`, {
          headers: this.headers,
          body: {
            phone: l,
            data: (n = o == null ? void 0 : o.data) !== null && n !== void 0 ? n : {},
            create_user: (i = o == null ? void 0 : o.shouldCreateUser) !== null && i !== void 0 ? i : !0,
            gotrue_meta_security: { captcha_token: o == null ? void 0 : o.captchaToken },
            channel: (a = o == null ? void 0 : o.channel) !== null && a !== void 0 ? a : "sms"
          }
        });
        return { data: { user: null, session: null, messageId: c == null ? void 0 : c.message_id }, error: u };
      }
      throw new It("You must provide either an email or phone number.");
    } catch (l) {
      if (N(l))
        return { data: { user: null, session: null }, error: l };
      throw l;
    }
  }
  /**
   * Log in a user given a User supplied OTP or TokenHash received through mobile or email.
   */
  async verifyOtp(e) {
    var t, s;
    try {
      let n, i;
      "options" in e && (n = (t = e.options) === null || t === void 0 ? void 0 : t.redirectTo, i = (s = e.options) === null || s === void 0 ? void 0 : s.captchaToken);
      const { data: a, error: l } = await G(this.fetch, "POST", `${this.url}/verify`, {
        headers: this.headers,
        body: Object.assign(Object.assign({}, e), { gotrue_meta_security: { captcha_token: i } }),
        redirectTo: n,
        xform: Te
      });
      if (l)
        throw l;
      if (!a)
        throw new Error("An error occurred on token verification.");
      const o = a.session, c = a.user;
      return o != null && o.access_token && (await this._saveSession(o), await this._notifyAllSubscribers(e.type == "recovery" ? "PASSWORD_RECOVERY" : "SIGNED_IN", o)), { data: { user: c, session: o }, error: null };
    } catch (n) {
      if (N(n))
        return { data: { user: null, session: null }, error: n };
      throw n;
    }
  }
  /**
   * Attempts a single-sign on using an enterprise Identity Provider. A
   * successful SSO attempt will redirect the current page to the identity
   * provider authorization page. The redirect URL is implementation and SSO
   * protocol specific.
   *
   * You can use it by providing a SSO domain. Typically you can extract this
   * domain by asking users for their email address. If this domain is
   * registered on the Auth instance the redirect will use that organization's
   * currently active SSO Identity Provider for the login.
   *
   * If you have built an organization-specific login page, you can use the
   * organization's SSO Identity Provider UUID directly instead.
   */
  async signInWithSSO(e) {
    var t, s, n;
    try {
      let i = null, a = null;
      return this.flowType === "pkce" && ([i, a] = await Ke(this.storage, this.storageKey)), await G(this.fetch, "POST", `${this.url}/sso`, {
        body: Object.assign(Object.assign(Object.assign(Object.assign(Object.assign({}, "providerId" in e ? { provider_id: e.providerId } : null), "domain" in e ? { domain: e.domain } : null), { redirect_to: (s = (t = e.options) === null || t === void 0 ? void 0 : t.redirectTo) !== null && s !== void 0 ? s : void 0 }), !((n = e == null ? void 0 : e.options) === null || n === void 0) && n.captchaToken ? { gotrue_meta_security: { captcha_token: e.options.captchaToken } } : null), { skip_http_redirect: !0, code_challenge: i, code_challenge_method: a }),
        headers: this.headers,
        xform: Ca
      });
    } catch (i) {
      if (N(i))
        return { data: null, error: i };
      throw i;
    }
  }
  /**
   * Sends a reauthentication OTP to the user's email or phone number.
   * Requires the user to be signed-in.
   */
  async reauthenticate() {
    return await this.initializePromise, await this._acquireLock(-1, async () => await this._reauthenticate());
  }
  async _reauthenticate() {
    try {
      return await this._useSession(async (e) => {
        const { data: { session: t }, error: s } = e;
        if (s)
          throw s;
        if (!t)
          throw new Ce();
        const { error: n } = await G(this.fetch, "GET", `${this.url}/reauthenticate`, {
          headers: this.headers,
          jwt: t.access_token
        });
        return { data: { user: null, session: null }, error: n };
      });
    } catch (e) {
      if (N(e))
        return { data: { user: null, session: null }, error: e };
      throw e;
    }
  }
  /**
   * Resends an existing signup confirmation email, email change email, SMS OTP or phone change OTP.
   */
  async resend(e) {
    try {
      const t = `${this.url}/resend`;
      if ("email" in e) {
        const { email: s, type: n, options: i } = e, { error: a } = await G(this.fetch, "POST", t, {
          headers: this.headers,
          body: {
            email: s,
            type: n,
            gotrue_meta_security: { captcha_token: i == null ? void 0 : i.captchaToken }
          },
          redirectTo: i == null ? void 0 : i.emailRedirectTo
        });
        return { data: { user: null, session: null }, error: a };
      } else if ("phone" in e) {
        const { phone: s, type: n, options: i } = e, { data: a, error: l } = await G(this.fetch, "POST", t, {
          headers: this.headers,
          body: {
            phone: s,
            type: n,
            gotrue_meta_security: { captcha_token: i == null ? void 0 : i.captchaToken }
          }
        });
        return { data: { user: null, session: null, messageId: a == null ? void 0 : a.message_id }, error: l };
      }
      throw new It("You must provide either an email or phone number and a type");
    } catch (t) {
      if (N(t))
        return { data: { user: null, session: null }, error: t };
      throw t;
    }
  }
  /**
   * Returns the session, refreshing it if necessary.
   *
   * The session returned can be null if the session is not detected which can happen in the event a user is not signed-in or has logged out.
   *
   * **IMPORTANT:** This method loads values directly from the storage attached
   * to the client. If that storage is based on request cookies for example,
   * the values in it may not be authentic and therefore it's strongly advised
   * against using this method and its results in such circumstances. A warning
   * will be emitted if this is detected. Use {@link #getUser()} instead.
   */
  async getSession() {
    return await this.initializePromise, await this._acquireLock(-1, async () => this._useSession(async (t) => t));
  }
  /**
   * Acquires a global lock based on the storage key.
   */
  async _acquireLock(e, t) {
    this._debug("#_acquireLock", "begin", e);
    try {
      if (this.lockAcquired) {
        const s = this.pendingInLock.length ? this.pendingInLock[this.pendingInLock.length - 1] : Promise.resolve(), n = (async () => (await s, await t()))();
        return this.pendingInLock.push((async () => {
          try {
            await n;
          } catch {
          }
        })()), n;
      }
      return await this.lock(`lock:${this.storageKey}`, e, async () => {
        this._debug("#_acquireLock", "lock acquired for storage key", this.storageKey);
        try {
          this.lockAcquired = !0;
          const s = t();
          for (this.pendingInLock.push((async () => {
            try {
              await s;
            } catch {
            }
          })()), await s; this.pendingInLock.length; ) {
            const n = [...this.pendingInLock];
            await Promise.all(n), this.pendingInLock.splice(0, n.length);
          }
          return await s;
        } finally {
          this._debug("#_acquireLock", "lock released for storage key", this.storageKey), this.lockAcquired = !1;
        }
      });
    } finally {
      this._debug("#_acquireLock", "end");
    }
  }
  /**
   * Use instead of {@link #getSession} inside the library. It is
   * semantically usually what you want, as getting a session involves some
   * processing afterwards that requires only one client operating on the
   * session at once across multiple tabs or processes.
   */
  async _useSession(e) {
    this._debug("#_useSession", "begin");
    try {
      const t = await this.__loadSession();
      return await e(t);
    } finally {
      this._debug("#_useSession", "end");
    }
  }
  /**
   * NEVER USE DIRECTLY!
   *
   * Always use {@link #_useSession}.
   */
  async __loadSession() {
    this._debug("#__loadSession()", "begin"), this.lockAcquired || this._debug("#__loadSession()", "used outside of an acquired lock!", new Error().stack);
    try {
      let e = null;
      const t = await wt(this.storage, this.storageKey);
      if (this._debug("#getSession()", "session from storage", t), t !== null && (this._isValidSession(t) ? e = t : (this._debug("#getSession()", "session from storage is not valid"), await this._removeSession())), !e)
        return { data: { session: null }, error: null };
      const s = e.expires_at ? e.expires_at * 1e3 - Date.now() < $t : !1;
      if (this._debug("#__loadSession()", `session has${s ? "" : " not"} expired`, "expires_at", e.expires_at), !s) {
        if (this.storage.isServer) {
          let a = this.suppressGetSessionWarning;
          e = new Proxy(e, {
            get: (o, c, u) => (!a && c === "user" && (console.warn("Using the user object as returned from supabase.auth.getSession() or from some supabase.auth.onAuthStateChange() events could be insecure! This value comes directly from the storage medium (usually cookies on the server) and may not be authentic. Use supabase.auth.getUser() instead which authenticates the data by contacting the Supabase Auth server."), a = !0, this.suppressGetSessionWarning = !0), Reflect.get(o, c, u))
          });
        }
        return { data: { session: e }, error: null };
      }
      const { session: n, error: i } = await this._callRefreshToken(e.refresh_token);
      return i ? { data: { session: null }, error: i } : { data: { session: n }, error: null };
    } finally {
      this._debug("#__loadSession()", "end");
    }
  }
  /**
   * Gets the current user details if there is an existing session. This method
   * performs a network request to the Supabase Auth server, so the returned
   * value is authentic and can be used to base authorization rules on.
   *
   * @param jwt Takes in an optional access token JWT. If no JWT is provided, the JWT from the current session is used.
   */
  async getUser(e) {
    return e ? await this._getUser(e) : (await this.initializePromise, await this._acquireLock(-1, async () => await this._getUser()));
  }
  async _getUser(e) {
    try {
      return e ? await G(this.fetch, "GET", `${this.url}/user`, {
        headers: this.headers,
        jwt: e,
        xform: ke
      }) : await this._useSession(async (t) => {
        var s, n, i;
        const { data: a, error: l } = t;
        if (l)
          throw l;
        return !(!((s = a.session) === null || s === void 0) && s.access_token) && !this.hasCustomAuthorizationHeader ? { data: { user: null }, error: new Ce() } : await G(this.fetch, "GET", `${this.url}/user`, {
          headers: this.headers,
          jwt: (i = (n = a.session) === null || n === void 0 ? void 0 : n.access_token) !== null && i !== void 0 ? i : void 0,
          xform: ke
        });
      });
    } catch (t) {
      if (N(t))
        return ya(t) && (await this._removeSession(), await St(this.storage, `${this.storageKey}-code-verifier`)), { data: { user: null }, error: t };
      throw t;
    }
  }
  /**
   * Updates user data for a logged in user.
   */
  async updateUser(e, t = {}) {
    return await this.initializePromise, await this._acquireLock(-1, async () => await this._updateUser(e, t));
  }
  async _updateUser(e, t = {}) {
    try {
      return await this._useSession(async (s) => {
        const { data: n, error: i } = s;
        if (i)
          throw i;
        if (!n.session)
          throw new Ce();
        const a = n.session;
        let l = null, o = null;
        this.flowType === "pkce" && e.email != null && ([l, o] = await Ke(this.storage, this.storageKey));
        const { data: c, error: u } = await G(this.fetch, "PUT", `${this.url}/user`, {
          headers: this.headers,
          redirectTo: t == null ? void 0 : t.emailRedirectTo,
          body: Object.assign(Object.assign({}, e), { code_challenge: l, code_challenge_method: o }),
          jwt: a.access_token,
          xform: ke
        });
        if (u)
          throw u;
        return a.user = c.user, await this._saveSession(a), await this._notifyAllSubscribers("USER_UPDATED", a), { data: { user: a.user }, error: null };
      });
    } catch (s) {
      if (N(s))
        return { data: { user: null }, error: s };
      throw s;
    }
  }
  /**
   * Decodes a JWT (without performing any validation).
   */
  _decodeJWT(e) {
    return zs(e);
  }
  /**
   * Sets the session data from the current session. If the current session is expired, setSession will take care of refreshing it to obtain a new session.
   * If the refresh token or access token in the current session is invalid, an error will be thrown.
   * @param currentSession The current session that minimally contains an access token and refresh token.
   */
  async setSession(e) {
    return await this.initializePromise, await this._acquireLock(-1, async () => await this._setSession(e));
  }
  async _setSession(e) {
    try {
      if (!e.access_token || !e.refresh_token)
        throw new Ce();
      const t = Date.now() / 1e3;
      let s = t, n = !0, i = null;
      const a = zs(e.access_token);
      if (a.exp && (s = a.exp, n = s <= t), n) {
        const { session: l, error: o } = await this._callRefreshToken(e.refresh_token);
        if (o)
          return { data: { user: null, session: null }, error: o };
        if (!l)
          return { data: { user: null, session: null }, error: null };
        i = l;
      } else {
        const { data: l, error: o } = await this._getUser(e.access_token);
        if (o)
          throw o;
        i = {
          access_token: e.access_token,
          refresh_token: e.refresh_token,
          user: l.user,
          token_type: "bearer",
          expires_in: s - t,
          expires_at: s
        }, await this._saveSession(i), await this._notifyAllSubscribers("SIGNED_IN", i);
      }
      return { data: { user: i.user, session: i }, error: null };
    } catch (t) {
      if (N(t))
        return { data: { session: null, user: null }, error: t };
      throw t;
    }
  }
  /**
   * Returns a new session, regardless of expiry status.
   * Takes in an optional current session. If not passed in, then refreshSession() will attempt to retrieve it from getSession().
   * If the current session's refresh token is invalid, an error will be thrown.
   * @param currentSession The current session. If passed in, it must contain a refresh token.
   */
  async refreshSession(e) {
    return await this.initializePromise, await this._acquireLock(-1, async () => await this._refreshSession(e));
  }
  async _refreshSession(e) {
    try {
      return await this._useSession(async (t) => {
        var s;
        if (!e) {
          const { data: a, error: l } = t;
          if (l)
            throw l;
          e = (s = a.session) !== null && s !== void 0 ? s : void 0;
        }
        if (!(e != null && e.refresh_token))
          throw new Ce();
        const { session: n, error: i } = await this._callRefreshToken(e.refresh_token);
        return i ? { data: { user: null, session: null }, error: i } : n ? { data: { user: n.user, session: n }, error: null } : { data: { user: null, session: null }, error: null };
      });
    } catch (t) {
      if (N(t))
        return { data: { user: null, session: null }, error: t };
      throw t;
    }
  }
  /**
   * Gets the session data from a URL string
   */
  async _getSessionFromURL(e, t) {
    try {
      if (!Se())
        throw new At("No browser detected.");
      if (e.error || e.error_description || e.error_code)
        throw new At(e.error_description || "Error in URL with unspecified error_description", {
          error: e.error || "unspecified_error",
          code: e.error_code || "unspecified_code"
        });
      switch (t) {
        case "implicit":
          if (this.flowType === "pkce")
            throw new xs("Not a valid PKCE flow url.");
          break;
        case "pkce":
          if (this.flowType === "implicit")
            throw new At("Not a valid implicit grant flow url.");
          break;
        default:
      }
      if (t === "pkce") {
        if (this._debug("#_initialize()", "begin", "is PKCE flow", !0), !e.code)
          throw new xs("No code detected.");
        const { data: A, error: y } = await this._exchangeCodeForSession(e.code);
        if (y)
          throw y;
        const O = new URL(window.location.href);
        return O.searchParams.delete("code"), window.history.replaceState(window.history.state, "", O.toString()), { data: { session: A.session, redirectType: null }, error: null };
      }
      const { provider_token: s, provider_refresh_token: n, access_token: i, refresh_token: a, expires_in: l, expires_at: o, token_type: c } = e;
      if (!i || !l || !a || !c)
        throw new At("No session defined in URL");
      const u = Math.round(Date.now() / 1e3), h = parseInt(l);
      let d = u + h;
      o && (d = parseInt(o));
      const _ = d - u;
      _ * 1e3 <= Qe && console.warn(`@supabase/gotrue-js: Session as retrieved from URL expires in ${_}s, should have been closer to ${h}s`);
      const p = d - h;
      u - p >= 120 ? console.warn("@supabase/gotrue-js: Session as retrieved from URL was issued over 120s ago, URL could be stale", p, d, u) : u - p < 0 && console.warn("@supabase/gotrue-js: Session as retrieved from URL was issued in the future? Check the device clock for skew", p, d, u);
      const { data: v, error: w } = await this._getUser(i);
      if (w)
        throw w;
      const S = {
        provider_token: s,
        provider_refresh_token: n,
        access_token: i,
        expires_in: h,
        expires_at: d,
        refresh_token: a,
        token_type: c,
        user: v.user
      };
      return window.location.hash = "", this._debug("#_getSessionFromURL()", "clearing window.location.hash"), { data: { session: S, redirectType: e.type }, error: null };
    } catch (s) {
      if (N(s))
        return { data: { session: null, redirectType: null }, error: s };
      throw s;
    }
  }
  /**
   * Checks if the current URL contains parameters given by an implicit oauth grant flow (https://www.rfc-editor.org/rfc/rfc6749.html#section-4.2)
   */
  _isImplicitGrantCallback(e) {
    return !!(e.access_token || e.error_description);
  }
  /**
   * Checks if the current URL and backing storage contain parameters given by a PKCE flow
   */
  async _isPKCECallback(e) {
    const t = await wt(this.storage, `${this.storageKey}-code-verifier`);
    return !!(e.code && t);
  }
  /**
   * Inside a browser context, `signOut()` will remove the logged in user from the browser session and log them out - removing all items from localstorage and then trigger a `"SIGNED_OUT"` event.
   *
   * For server-side management, you can revoke all refresh tokens for a user by passing a user's JWT through to `auth.api.signOut(JWT: string)`.
   * There is no way to revoke a user's access token jwt until it expires. It is recommended to set a shorter expiry on the jwt for this reason.
   *
   * If using `others` scope, no `SIGNED_OUT` event is fired!
   */
  async signOut(e = { scope: "global" }) {
    return await this.initializePromise, await this._acquireLock(-1, async () => await this._signOut(e));
  }
  async _signOut({ scope: e } = { scope: "global" }) {
    return await this._useSession(async (t) => {
      var s;
      const { data: n, error: i } = t;
      if (i)
        return { error: i };
      const a = (s = n.session) === null || s === void 0 ? void 0 : s.access_token;
      if (a) {
        const { error: l } = await this.admin.signOut(a, e);
        if (l && !(ba(l) && (l.status === 404 || l.status === 401 || l.status === 403)))
          return { error: l };
      }
      return e !== "others" && (await this._removeSession(), await St(this.storage, `${this.storageKey}-code-verifier`)), { error: null };
    });
  }
  /**
   * Receive a notification every time an auth event happens.
   * @param callback A callback function to be invoked when an auth event happens.
   */
  onAuthStateChange(e) {
    const t = aa(), s = {
      id: t,
      callback: e,
      unsubscribe: () => {
        this._debug("#unsubscribe()", "state change callback with id removed", t), this.stateChangeEmitters.delete(t);
      }
    };
    return this._debug("#onAuthStateChange()", "registered callback with id", t), this.stateChangeEmitters.set(t, s), (async () => (await this.initializePromise, await this._acquireLock(-1, async () => {
      this._emitInitialSession(t);
    })))(), { data: { subscription: s } };
  }
  async _emitInitialSession(e) {
    return await this._useSession(async (t) => {
      var s, n;
      try {
        const { data: { session: i }, error: a } = t;
        if (a)
          throw a;
        await ((s = this.stateChangeEmitters.get(e)) === null || s === void 0 ? void 0 : s.callback("INITIAL_SESSION", i)), this._debug("INITIAL_SESSION", "callback id", e, "session", i);
      } catch (i) {
        await ((n = this.stateChangeEmitters.get(e)) === null || n === void 0 ? void 0 : n.callback("INITIAL_SESSION", null)), this._debug("INITIAL_SESSION", "callback id", e, "error", i), console.error(i);
      }
    });
  }
  /**
   * Sends a password reset request to an email address. This method supports the PKCE flow.
   *
   * @param email The email address of the user.
   * @param options.redirectTo The URL to send the user to after they click the password reset link.
   * @param options.captchaToken Verification token received when the user completes the captcha on the site.
   */
  async resetPasswordForEmail(e, t = {}) {
    let s = null, n = null;
    this.flowType === "pkce" && ([s, n] = await Ke(
      this.storage,
      this.storageKey,
      !0
      // isPasswordRecovery
    ));
    try {
      return await G(this.fetch, "POST", `${this.url}/recover`, {
        body: {
          email: e,
          code_challenge: s,
          code_challenge_method: n,
          gotrue_meta_security: { captcha_token: t.captchaToken }
        },
        headers: this.headers,
        redirectTo: t.redirectTo
      });
    } catch (i) {
      if (N(i))
        return { data: null, error: i };
      throw i;
    }
  }
  /**
   * Gets all the identities linked to a user.
   */
  async getUserIdentities() {
    var e;
    try {
      const { data: t, error: s } = await this.getUser();
      if (s)
        throw s;
      return { data: { identities: (e = t.user.identities) !== null && e !== void 0 ? e : [] }, error: null };
    } catch (t) {
      if (N(t))
        return { data: null, error: t };
      throw t;
    }
  }
  /**
   * Links an oauth identity to an existing user.
   * This method supports the PKCE flow.
   */
  async linkIdentity(e) {
    var t;
    try {
      const { data: s, error: n } = await this._useSession(async (i) => {
        var a, l, o, c, u;
        const { data: h, error: d } = i;
        if (d)
          throw d;
        const _ = await this._getUrlForProvider(`${this.url}/user/identities/authorize`, e.provider, {
          redirectTo: (a = e.options) === null || a === void 0 ? void 0 : a.redirectTo,
          scopes: (l = e.options) === null || l === void 0 ? void 0 : l.scopes,
          queryParams: (o = e.options) === null || o === void 0 ? void 0 : o.queryParams,
          skipBrowserRedirect: !0
        });
        return await G(this.fetch, "GET", _, {
          headers: this.headers,
          jwt: (u = (c = h.session) === null || c === void 0 ? void 0 : c.access_token) !== null && u !== void 0 ? u : void 0
        });
      });
      if (n)
        throw n;
      return Se() && !(!((t = e.options) === null || t === void 0) && t.skipBrowserRedirect) && window.location.assign(s == null ? void 0 : s.url), { data: { provider: e.provider, url: s == null ? void 0 : s.url }, error: null };
    } catch (s) {
      if (N(s))
        return { data: { provider: e.provider, url: null }, error: s };
      throw s;
    }
  }
  /**
   * Unlinks an identity from a user by deleting it. The user will no longer be able to sign in with that identity once it's unlinked.
   */
  async unlinkIdentity(e) {
    try {
      return await this._useSession(async (t) => {
        var s, n;
        const { data: i, error: a } = t;
        if (a)
          throw a;
        return await G(this.fetch, "DELETE", `${this.url}/user/identities/${e.identity_id}`, {
          headers: this.headers,
          jwt: (n = (s = i.session) === null || s === void 0 ? void 0 : s.access_token) !== null && n !== void 0 ? n : void 0
        });
      });
    } catch (t) {
      if (N(t))
        return { data: null, error: t };
      throw t;
    }
  }
  /**
   * Generates a new JWT.
   * @param refreshToken A valid refresh token that was returned on login.
   */
  async _refreshAccessToken(e) {
    const t = `#_refreshAccessToken(${e.substring(0, 5)}...)`;
    this._debug(t, "begin");
    try {
      const s = Date.now();
      return await ha(async (n) => (n > 0 && await ua(200 * Math.pow(2, n - 1)), this._debug(t, "refreshing attempt", n), await G(this.fetch, "POST", `${this.url}/token?grant_type=refresh_token`, {
        body: { refresh_token: e },
        headers: this.headers,
        xform: Te
      })), (n, i) => {
        const a = 200 * Math.pow(2, n);
        return i && Gt(i) && // retryable only if the request can be sent before the backoff overflows the tick duration
        Date.now() + a - s < Qe;
      });
    } catch (s) {
      if (this._debug(t, "error", s), N(s))
        return { data: { session: null, user: null }, error: s };
      throw s;
    } finally {
      this._debug(t, "end");
    }
  }
  _isValidSession(e) {
    return typeof e == "object" && e !== null && "access_token" in e && "refresh_token" in e && "expires_at" in e;
  }
  async _handleProviderSignIn(e, t) {
    const s = await this._getUrlForProvider(`${this.url}/authorize`, e, {
      redirectTo: t.redirectTo,
      scopes: t.scopes,
      queryParams: t.queryParams
    });
    return this._debug("#_handleProviderSignIn()", "provider", e, "options", t, "url", s), Se() && !t.skipBrowserRedirect && window.location.assign(s), { data: { provider: e, url: s }, error: null };
  }
  /**
   * Recovers the session from LocalStorage and refreshes the token
   * Note: this method is async to accommodate for AsyncStorage e.g. in React native.
   */
  async _recoverAndRefresh() {
    var e;
    const t = "#_recoverAndRefresh()";
    this._debug(t, "begin");
    try {
      const s = await wt(this.storage, this.storageKey);
      if (this._debug(t, "session from storage", s), !this._isValidSession(s)) {
        this._debug(t, "session is not valid"), s !== null && await this._removeSession();
        return;
      }
      const n = ((e = s.expires_at) !== null && e !== void 0 ? e : 1 / 0) * 1e3 - Date.now() < $t;
      if (this._debug(t, `session has${n ? "" : " not"} expired with margin of ${$t}s`), n) {
        if (this.autoRefreshToken && s.refresh_token) {
          const { error: i } = await this._callRefreshToken(s.refresh_token);
          i && (console.error(i), Gt(i) || (this._debug(t, "refresh failed with a non-retryable error, removing the session", i), await this._removeSession()));
        }
      } else
        await this._notifyAllSubscribers("SIGNED_IN", s);
    } catch (s) {
      this._debug(t, "error", s), console.error(s);
      return;
    } finally {
      this._debug(t, "end");
    }
  }
  async _callRefreshToken(e) {
    var t, s;
    if (!e)
      throw new Ce();
    if (this.refreshingDeferred)
      return this.refreshingDeferred.promise;
    const n = `#_callRefreshToken(${e.substring(0, 5)}...)`;
    this._debug(n, "begin");
    try {
      this.refreshingDeferred = new Nt();
      const { data: i, error: a } = await this._refreshAccessToken(e);
      if (a)
        throw a;
      if (!i.session)
        throw new Ce();
      await this._saveSession(i.session), await this._notifyAllSubscribers("TOKEN_REFRESHED", i.session);
      const l = { session: i.session, error: null };
      return this.refreshingDeferred.resolve(l), l;
    } catch (i) {
      if (this._debug(n, "error", i), N(i)) {
        const a = { session: null, error: i };
        return Gt(i) || await this._removeSession(), (t = this.refreshingDeferred) === null || t === void 0 || t.resolve(a), a;
      }
      throw (s = this.refreshingDeferred) === null || s === void 0 || s.reject(i), i;
    } finally {
      this.refreshingDeferred = null, this._debug(n, "end");
    }
  }
  async _notifyAllSubscribers(e, t, s = !0) {
    const n = `#_notifyAllSubscribers(${e})`;
    this._debug(n, "begin", t, `broadcast = ${s}`);
    try {
      this.broadcastChannel && s && this.broadcastChannel.postMessage({ event: e, session: t });
      const i = [], a = Array.from(this.stateChangeEmitters.values()).map(async (l) => {
        try {
          await l.callback(e, t);
        } catch (o) {
          i.push(o);
        }
      });
      if (await Promise.all(a), i.length > 0) {
        for (let l = 0; l < i.length; l += 1)
          console.error(i[l]);
        throw i[0];
      }
    } finally {
      this._debug(n, "end");
    }
  }
  /**
   * set currentSession and currentUser
   * process to _startAutoRefreshToken if possible
   */
  async _saveSession(e) {
    this._debug("#_saveSession()", e), this.suppressGetSessionWarning = !0, await Wr(this.storage, this.storageKey, e);
  }
  async _removeSession() {
    this._debug("#_removeSession()"), await St(this.storage, this.storageKey), await this._notifyAllSubscribers("SIGNED_OUT", null);
  }
  /**
   * Removes any registered visibilitychange callback.
   *
   * {@see #startAutoRefresh}
   * {@see #stopAutoRefresh}
   */
  _removeVisibilityChangedCallback() {
    this._debug("#_removeVisibilityChangedCallback()");
    const e = this.visibilityChangedCallback;
    this.visibilityChangedCallback = null;
    try {
      e && Se() && (window != null && window.removeEventListener) && window.removeEventListener("visibilitychange", e);
    } catch (t) {
      console.error("removing visibilitychange callback failed", t);
    }
  }
  /**
   * This is the private implementation of {@link #startAutoRefresh}. Use this
   * within the library.
   */
  async _startAutoRefresh() {
    await this._stopAutoRefresh(), this._debug("#_startAutoRefresh()");
    const e = setInterval(() => this._autoRefreshTokenTick(), Qe);
    this.autoRefreshTicker = e, e && typeof e == "object" && typeof e.unref == "function" ? e.unref() : typeof Deno < "u" && typeof Deno.unrefTimer == "function" && Deno.unrefTimer(e), setTimeout(async () => {
      await this.initializePromise, await this._autoRefreshTokenTick();
    }, 0);
  }
  /**
   * This is the private implementation of {@link #stopAutoRefresh}. Use this
   * within the library.
   */
  async _stopAutoRefresh() {
    this._debug("#_stopAutoRefresh()");
    const e = this.autoRefreshTicker;
    this.autoRefreshTicker = null, e && clearInterval(e);
  }
  /**
   * Starts an auto-refresh process in the background. The session is checked
   * every few seconds. Close to the time of expiration a process is started to
   * refresh the session. If refreshing fails it will be retried for as long as
   * necessary.
   *
   * If you set the {@link GoTrueClientOptions#autoRefreshToken} you don't need
   * to call this function, it will be called for you.
   *
   * On browsers the refresh process works only when the tab/window is in the
   * foreground to conserve resources as well as prevent race conditions and
   * flooding auth with requests. If you call this method any managed
   * visibility change callback will be removed and you must manage visibility
   * changes on your own.
   *
   * On non-browser platforms the refresh process works *continuously* in the
   * background, which may not be desirable. You should hook into your
   * platform's foreground indication mechanism and call these methods
   * appropriately to conserve resources.
   *
   * {@see #stopAutoRefresh}
   */
  async startAutoRefresh() {
    this._removeVisibilityChangedCallback(), await this._startAutoRefresh();
  }
  /**
   * Stops an active auto refresh process running in the background (if any).
   *
   * If you call this method any managed visibility change callback will be
   * removed and you must manage visibility changes on your own.
   *
   * See {@link #startAutoRefresh} for more details.
   */
  async stopAutoRefresh() {
    this._removeVisibilityChangedCallback(), await this._stopAutoRefresh();
  }
  /**
   * Runs the auto refresh token tick.
   */
  async _autoRefreshTokenTick() {
    this._debug("#_autoRefreshTokenTick()", "begin");
    try {
      await this._acquireLock(0, async () => {
        try {
          const e = Date.now();
          try {
            return await this._useSession(async (t) => {
              const { data: { session: s } } = t;
              if (!s || !s.refresh_token || !s.expires_at) {
                this._debug("#_autoRefreshTokenTick()", "no session");
                return;
              }
              const n = Math.floor((s.expires_at * 1e3 - e) / Qe);
              this._debug("#_autoRefreshTokenTick()", `access token expires in ${n} ticks, a tick lasts ${Qe}ms, refresh threshold is ${es} ticks`), n <= es && await this._callRefreshToken(s.refresh_token);
            });
          } catch (t) {
            console.error("Auto refresh tick failed with error. This is likely a transient error.", t);
          }
        } finally {
          this._debug("#_autoRefreshTokenTick()", "end");
        }
      });
    } catch (e) {
      if (e.isAcquireTimeout || e instanceof Nr)
        this._debug("auto refresh token tick lock not available");
      else
        throw e;
    }
  }
  /**
   * Registers callbacks on the browser / platform, which in-turn run
   * algorithms when the browser window/tab are in foreground. On non-browser
   * platforms it assumes always foreground.
   */
  async _handleVisibilityChange() {
    if (this._debug("#_handleVisibilityChange()"), !Se() || !(window != null && window.addEventListener))
      return this.autoRefreshToken && this.startAutoRefresh(), !1;
    try {
      this.visibilityChangedCallback = async () => await this._onVisibilityChanged(!1), window == null || window.addEventListener("visibilitychange", this.visibilityChangedCallback), await this._onVisibilityChanged(!0);
    } catch (e) {
      console.error("_handleVisibilityChange", e);
    }
  }
  /**
   * Callback registered with `window.addEventListener('visibilitychange')`.
   */
  async _onVisibilityChanged(e) {
    const t = `#_onVisibilityChanged(${e})`;
    this._debug(t, "visibilityState", document.visibilityState), document.visibilityState === "visible" ? (this.autoRefreshToken && this._startAutoRefresh(), e || (await this.initializePromise, await this._acquireLock(-1, async () => {
      if (document.visibilityState !== "visible") {
        this._debug(t, "acquired the lock to recover the session, but the browser visibilityState is no longer visible, aborting");
        return;
      }
      await this._recoverAndRefresh();
    }))) : document.visibilityState === "hidden" && this.autoRefreshToken && this._stopAutoRefresh();
  }
  /**
   * Generates the relevant login URL for a third-party provider.
   * @param options.redirectTo A URL or mobile address to send the user to after they are confirmed.
   * @param options.scopes A space-separated list of scopes granted to the OAuth application.
   * @param options.queryParams An object of key-value pairs containing query parameters granted to the OAuth application.
   */
  async _getUrlForProvider(e, t, s) {
    const n = [`provider=${encodeURIComponent(t)}`];
    if (s != null && s.redirectTo && n.push(`redirect_to=${encodeURIComponent(s.redirectTo)}`), s != null && s.scopes && n.push(`scopes=${encodeURIComponent(s.scopes)}`), this.flowType === "pkce") {
      const [i, a] = await Ke(this.storage, this.storageKey), l = new URLSearchParams({
        code_challenge: `${encodeURIComponent(i)}`,
        code_challenge_method: `${encodeURIComponent(a)}`
      });
      n.push(l.toString());
    }
    if (s != null && s.queryParams) {
      const i = new URLSearchParams(s.queryParams);
      n.push(i.toString());
    }
    return s != null && s.skipBrowserRedirect && n.push(`skip_http_redirect=${s.skipBrowserRedirect}`), `${e}?${n.join("&")}`;
  }
  async _unenroll(e) {
    try {
      return await this._useSession(async (t) => {
        var s;
        const { data: n, error: i } = t;
        return i ? { data: null, error: i } : await G(this.fetch, "DELETE", `${this.url}/factors/${e.factorId}`, {
          headers: this.headers,
          jwt: (s = n == null ? void 0 : n.session) === null || s === void 0 ? void 0 : s.access_token
        });
      });
    } catch (t) {
      if (N(t))
        return { data: null, error: t };
      throw t;
    }
  }
  async _enroll(e) {
    try {
      return await this._useSession(async (t) => {
        var s, n;
        const { data: i, error: a } = t;
        if (a)
          return { data: null, error: a };
        const l = Object.assign({ friendly_name: e.friendlyName, factor_type: e.factorType }, e.factorType === "phone" ? { phone: e.phone } : { issuer: e.issuer }), { data: o, error: c } = await G(this.fetch, "POST", `${this.url}/factors`, {
          body: l,
          headers: this.headers,
          jwt: (s = i == null ? void 0 : i.session) === null || s === void 0 ? void 0 : s.access_token
        });
        return c ? { data: null, error: c } : (e.factorType === "totp" && (!((n = o == null ? void 0 : o.totp) === null || n === void 0) && n.qr_code) && (o.totp.qr_code = `data:image/svg+xml;utf-8,${o.totp.qr_code}`), { data: o, error: null });
      });
    } catch (t) {
      if (N(t))
        return { data: null, error: t };
      throw t;
    }
  }
  /**
   * {@see GoTrueMFAApi#verify}
   */
  async _verify(e) {
    return this._acquireLock(-1, async () => {
      try {
        return await this._useSession(async (t) => {
          var s;
          const { data: n, error: i } = t;
          if (i)
            return { data: null, error: i };
          const { data: a, error: l } = await G(this.fetch, "POST", `${this.url}/factors/${e.factorId}/verify`, {
            body: { code: e.code, challenge_id: e.challengeId },
            headers: this.headers,
            jwt: (s = n == null ? void 0 : n.session) === null || s === void 0 ? void 0 : s.access_token
          });
          return l ? { data: null, error: l } : (await this._saveSession(Object.assign({ expires_at: Math.round(Date.now() / 1e3) + a.expires_in }, a)), await this._notifyAllSubscribers("MFA_CHALLENGE_VERIFIED", a), { data: a, error: l });
        });
      } catch (t) {
        if (N(t))
          return { data: null, error: t };
        throw t;
      }
    });
  }
  /**
   * {@see GoTrueMFAApi#challenge}
   */
  async _challenge(e) {
    return this._acquireLock(-1, async () => {
      try {
        return await this._useSession(async (t) => {
          var s;
          const { data: n, error: i } = t;
          return i ? { data: null, error: i } : await G(this.fetch, "POST", `${this.url}/factors/${e.factorId}/challenge`, {
            body: { channel: e.channel },
            headers: this.headers,
            jwt: (s = n == null ? void 0 : n.session) === null || s === void 0 ? void 0 : s.access_token
          });
        });
      } catch (t) {
        if (N(t))
          return { data: null, error: t };
        throw t;
      }
    });
  }
  /**
   * {@see GoTrueMFAApi#challengeAndVerify}
   */
  async _challengeAndVerify(e) {
    const { data: t, error: s } = await this._challenge({
      factorId: e.factorId
    });
    return s ? { data: null, error: s } : await this._verify({
      factorId: e.factorId,
      challengeId: t.id,
      code: e.code
    });
  }
  /**
   * {@see GoTrueMFAApi#listFactors}
   */
  async _listFactors() {
    const { data: { user: e }, error: t } = await this.getUser();
    if (t)
      return { data: null, error: t };
    const s = (e == null ? void 0 : e.factors) || [], n = s.filter((a) => a.factor_type === "totp" && a.status === "verified"), i = s.filter((a) => a.factor_type === "phone" && a.status === "verified");
    return {
      data: {
        all: s,
        totp: n,
        phone: i
      },
      error: null
    };
  }
  /**
   * {@see GoTrueMFAApi#getAuthenticatorAssuranceLevel}
   */
  async _getAuthenticatorAssuranceLevel() {
    return this._acquireLock(-1, async () => await this._useSession(async (e) => {
      var t, s;
      const { data: { session: n }, error: i } = e;
      if (i)
        return { data: null, error: i };
      if (!n)
        return {
          data: { currentLevel: null, nextLevel: null, currentAuthenticationMethods: [] },
          error: null
        };
      const a = this._decodeJWT(n.access_token);
      let l = null;
      a.aal && (l = a.aal);
      let o = l;
      ((s = (t = n.user.factors) === null || t === void 0 ? void 0 : t.filter((h) => h.status === "verified")) !== null && s !== void 0 ? s : []).length > 0 && (o = "aal2");
      const u = a.amr || [];
      return { data: { currentLevel: l, nextLevel: o, currentAuthenticationMethods: u }, error: null };
    }));
  }
}
gt.nextInstanceID = 0;
const Na = gt;
class Fa extends Na {
  constructor(e) {
    super(e);
  }
}
var Ma = function(r, e, t, s) {
  function n(i) {
    return i instanceof t ? i : new t(function(a) {
      a(i);
    });
  }
  return new (t || (t = Promise))(function(i, a) {
    function l(u) {
      try {
        c(s.next(u));
      } catch (h) {
        a(h);
      }
    }
    function o(u) {
      try {
        c(s.throw(u));
      } catch (h) {
        a(h);
      }
    }
    function c(u) {
      u.done ? i(u.value) : n(u.value).then(l, o);
    }
    c((s = s.apply(r, e || [])).next());
  });
};
class Ha {
  /**
   * Create a new client for use in the browser.
   * @param supabaseUrl The unique Supabase URL which is supplied when you create a new project in your project dashboard.
   * @param supabaseKey The unique Supabase Key which is supplied when you create a new project in your project dashboard.
   * @param options.db.schema You can switch in between schemas. The schema needs to be on the list of exposed schemas inside Supabase.
   * @param options.auth.autoRefreshToken Set to "true" if you want to automatically refresh the token before expiring.
   * @param options.auth.persistSession Set to "true" if you want to automatically save the user session into local storage.
   * @param options.auth.detectSessionInUrl Set to "true" if you want to automatically detects OAuth grants in the URL and signs in the user.
   * @param options.realtime Options passed along to realtime-js constructor.
   * @param options.global.fetch A custom fetch implementation.
   * @param options.global.headers Any additional headers to send with each network request.
   */
  constructor(e, t, s) {
    var n, i, a;
    if (this.supabaseUrl = e, this.supabaseKey = t, !e)
      throw new Error("supabaseUrl is required.");
    if (!t)
      throw new Error("supabaseKey is required.");
    const l = ea(e);
    this.realtimeUrl = `${l}/realtime/v1`.replace(/^http/i, "ws"), this.authUrl = `${l}/auth/v1`, this.storageUrl = `${l}/storage/v1`, this.functionsUrl = `${l}/functions/v1`;
    const o = `sb-${new URL(this.authUrl).hostname.split(".")[0]}-auth-token`, c = {
      db: zi,
      realtime: Ji,
      auth: Object.assign(Object.assign({}, xi), { storageKey: o }),
      global: qi
    }, u = ta(s ?? {}, c);
    this.storageKey = (n = u.auth.storageKey) !== null && n !== void 0 ? n : "", this.headers = (i = u.global.headers) !== null && i !== void 0 ? i : {}, u.accessToken ? (this.accessToken = u.accessToken, this.auth = new Proxy({}, {
      get: (h, d) => {
        throw new Error(`@supabase/supabase-js: Supabase Client is configured with the accessToken option, accessing supabase.auth.${String(d)} is not possible`);
      }
    })) : this.auth = this._initSupabaseAuthClient((a = u.auth) !== null && a !== void 0 ? a : {}, this.headers, u.global.fetch), this.fetch = Qi(t, this._getAccessToken.bind(this), u.global.fetch), this.realtime = this._initRealtimeClient(Object.assign({ headers: this.headers, accessToken: this._getAccessToken.bind(this) }, u.realtime)), this.rest = new fi(`${l}/rest/v1`, {
      headers: this.headers,
      schema: u.db.schema,
      fetch: this.fetch
    }), u.accessToken || this._listenForAuthEvents();
  }
  /**
   * Supabase Functions allows you to deploy and invoke edge functions.
   */
  get functions() {
    return new $n(this.functionsUrl, {
      headers: this.headers,
      customFetch: this.fetch
    });
  }
  /**
   * Supabase Storage allows you to manage user-generated content, such as photos or videos.
   */
  get storage() {
    return new $i(this.storageUrl, this.headers, this.fetch);
  }
  /**
   * Perform a query on a table or a view.
   *
   * @param relation - The table or view name to query
   */
  from(e) {
    return this.rest.from(e);
  }
  // NOTE: signatures must be kept in sync with PostgrestClient.schema
  /**
   * Select a schema to query or perform an function (rpc) call.
   *
   * The schema needs to be on the list of exposed schemas inside Supabase.
   *
   * @param schema - The schema to query
   */
  schema(e) {
    return this.rest.schema(e);
  }
  // NOTE: signatures must be kept in sync with PostgrestClient.rpc
  /**
   * Perform a function call.
   *
   * @param fn - The function name to call
   * @param args - The arguments to pass to the function call
   * @param options - Named parameters
   * @param options.head - When set to `true`, `data` will not be returned.
   * Useful if you only need the count.
   * @param options.get - When set to `true`, the function will be called with
   * read-only access mode.
   * @param options.count - Count algorithm to use to count rows returned by the
   * function. Only applicable for [set-returning
   * functions](https://www.postgresql.org/docs/current/functions-srf.html).
   *
   * `"exact"`: Exact but slow count algorithm. Performs a `COUNT(*)` under the
   * hood.
   *
   * `"planned"`: Approximated but fast count algorithm. Uses the Postgres
   * statistics under the hood.
   *
   * `"estimated"`: Uses exact count for low numbers and planned count for high
   * numbers.
   */
  rpc(e, t = {}, s = {}) {
    return this.rest.rpc(e, t, s);
  }
  /**
   * Creates a Realtime channel with Broadcast, Presence, and Postgres Changes.
   *
   * @param {string} name - The name of the Realtime channel.
   * @param {Object} opts - The options to pass to the Realtime channel.
   *
   */
  channel(e, t = { config: {} }) {
    return this.realtime.channel(e, t);
  }
  /**
   * Returns all Realtime channels.
   */
  getChannels() {
    return this.realtime.getChannels();
  }
  /**
   * Unsubscribes and removes Realtime channel from Realtime client.
   *
   * @param {RealtimeChannel} channel - The name of the Realtime channel.
   *
   */
  removeChannel(e) {
    return this.realtime.removeChannel(e);
  }
  /**
   * Unsubscribes and removes all Realtime channels from Realtime client.
   */
  removeAllChannels() {
    return this.realtime.removeAllChannels();
  }
  _getAccessToken() {
    var e, t;
    return Ma(this, void 0, void 0, function* () {
      if (this.accessToken)
        return yield this.accessToken();
      const { data: s } = yield this.auth.getSession();
      return (t = (e = s.session) === null || e === void 0 ? void 0 : e.access_token) !== null && t !== void 0 ? t : null;
    });
  }
  _initSupabaseAuthClient({ autoRefreshToken: e, persistSession: t, detectSessionInUrl: s, storage: n, storageKey: i, flowType: a, lock: l, debug: o }, c, u) {
    const h = {
      Authorization: `Bearer ${this.supabaseKey}`,
      apikey: `${this.supabaseKey}`
    };
    return new Fa({
      url: this.authUrl,
      headers: Object.assign(Object.assign({}, h), c),
      storageKey: i,
      autoRefreshToken: e,
      persistSession: t,
      detectSessionInUrl: s,
      storage: n,
      flowType: a,
      lock: l,
      debug: o,
      fetch: u,
      // auth checks if there is a custom authorizaiton header using this flag
      // so it knows whether to return an error when getUser is called with no session
      hasCustomAuthorizationHeader: "Authorization" in this.headers
    });
  }
  _initRealtimeClient(e) {
    return new Ti(this.realtimeUrl, Object.assign(Object.assign({}, e), { params: Object.assign({ apikey: this.supabaseKey }, e == null ? void 0 : e.params) }));
  }
  _listenForAuthEvents() {
    return this.auth.onAuthStateChange((t, s) => {
      this._handleTokenChanged(t, "CLIENT", s == null ? void 0 : s.access_token);
    });
  }
  _handleTokenChanged(e, t, s) {
    (e === "TOKEN_REFRESHED" || e === "SIGNED_IN") && this.changedAccessToken !== s ? this.changedAccessToken = s : e === "SIGNED_OUT" && (this.realtime.setAuth(), t == "STORAGE" && this.auth.signOut(), this.changedAccessToken = void 0);
  }
}
const $a = (r, e, t) => new Ha(r, e, t), Ba = { BASE_URL: "/", DEV: !1, MODE: "production", PROD: !0, SSR: !1, VITE_SUPABASE_ANON_KEY: void 0, VITE_SUPABASE_URL: void 0 }, Fr = "http://127.0.0.1:54321", Mr = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0";
console.log("Supabase Auth Config:", {
  haveUrl: !0,
  haveKey: !0,
  isDev: !1,
  url: Fr,
  keyPreview: Mr.substring(0, 10) + "...",
  env: Ba
});
const ct = $a(Fr, Mr, {
  auth: {
    persistSession: !0,
    autoRefreshToken: !0,
    storageKey: "supabase-auth-app"
  }
}), qt = {
  user: null,
  session: null,
  loading: !0,
  error: null
}, Ga = () => {
  const { subscribe: r, set: e, update: t } = gr(qt);
  return {
    subscribe: r,
    // Initialize auth - call this on app startup
    init: async () => {
      var s;
      try {
        const { data: n } = await ct.auth.getSession();
        e({
          user: ((s = n.session) == null ? void 0 : s.user) || null,
          session: n.session,
          loading: !1,
          error: null
        }), ct.auth.onAuthStateChange((i, a) => {
          t((l) => ({
            ...l,
            user: (a == null ? void 0 : a.user) || null,
            session: a,
            loading: !1
          })), a ? fetch("/api/auth/session", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ token: a.access_token })
          }) : fetch("/api/auth/session", { method: "DELETE" });
        });
      } catch (n) {
        console.error("Error initializing auth:", n), e({
          ...qt,
          loading: !1,
          error: n instanceof Error ? n.message : "Unknown error"
        });
      }
    },
    // Sign up with email and password
    signUp: async (s, n) => {
      t((i) => ({ ...i, loading: !0, error: null }));
      try {
        const { data: i, error: a } = await ct.auth.signUp({
          email: s,
          password: n
        });
        if (a) throw a;
        return t((l) => ({
          ...l,
          loading: !1,
          // If email confirmation is required, the user will be null here
          user: i.user,
          session: i.session,
          error: null
        })), { success: !0, needsConfirmation: !i.session };
      } catch (i) {
        return t((a) => ({
          ...a,
          loading: !1,
          error: i instanceof Error ? i.message : "Failed to sign up"
        })), { success: !1, message: i instanceof Error ? i.message : "Failed to sign up" };
      }
    },
    // Sign in with email and password
    signIn: async (s, n) => {
      t((i) => ({ ...i, loading: !0, error: null }));
      try {
        const { data: i, error: a } = await ct.auth.signInWithPassword({
          email: s,
          password: n
        });
        if (a) throw a;
        return t((l) => ({
          ...l,
          user: i.user,
          session: i.session,
          loading: !1,
          error: null
        })), { success: !0 };
      } catch (i) {
        return t((a) => ({
          ...a,
          loading: !1,
          error: i instanceof Error ? i.message : "Failed to sign in"
        })), { success: !1, message: i instanceof Error ? i.message : "Failed to sign in" };
      }
    },
    // Sign out current user
    signOut: async () => {
      t((s) => ({ ...s, loading: !0, error: null }));
      try {
        return await ct.auth.signOut(), t((s) => ({
          ...qt,
          loading: !1
        })), { success: !0 };
      } catch (s) {
        return t((n) => ({
          ...n,
          loading: !1,
          error: s instanceof Error ? s.message : "Failed to sign out"
        })), { success: !1, message: s instanceof Error ? s.message : "Failed to sign out" };
      }
    },
    // Clear auth errors
    clearError: () => {
      t((s) => ({ ...s, error: null }));
    }
  };
}, we = Ga(), qa = Pt(we, (r) => r.user), Hr = Pt(we, (r) => !!r.user), hs = Pt(we, (r) => r.loading), $r = Pt(we, (r) => r.error);
function Zs(r) {
  let e, t;
  return {
    c() {
      e = m("div"), t = k(
        /*formError*/
        r[2]
      ), this.h();
    },
    l(s) {
      e = b(s, "DIV", { class: !0 });
      var n = I(e);
      t = P(
        n,
        /*formError*/
        r[2]
      ), n.forEach(E), this.h();
    },
    h() {
      g(e, "class", "error-message svelte-s1y7y7");
    },
    m(s, n) {
      L(s, e, n), f(e, t);
    },
    p(s, n) {
      n & /*formError*/
      4 && M(
        t,
        /*formError*/
        s[2]
      );
    },
    d(s) {
      s && E(e);
    }
  };
}
function za(r) {
  let e, t, s = "Sign In", n, i, a, l, o, c = "Email", u, h, d, _, p, v = "Password", w, S, A, y, O = (
    /*loading*/
    r[3] ? "Signing in..." : "Sign In"
  ), C, D, F, V = (
    /*formError*/
    r[2] && Zs(r)
  );
  return {
    c() {
      e = m("div"), t = m("h2"), t.textContent = s, n = T(), V && V.c(), i = T(), a = m("form"), l = m("div"), o = m("label"), o.textContent = c, u = T(), h = m("input"), d = T(), _ = m("div"), p = m("label"), p.textContent = v, w = T(), S = m("input"), A = T(), y = m("button"), C = k(O), this.h();
    },
    l(W) {
      e = b(W, "DIV", { class: !0 });
      var U = I(e);
      t = b(U, "H2", { class: !0, "data-svelte-h": !0 }), Y(t) !== "svelte-1f1zcva" && (t.textContent = s), n = R(U), V && V.l(U), i = R(U), a = b(U, "FORM", {});
      var se = I(a);
      l = b(se, "DIV", { class: !0 });
      var le = I(l);
      o = b(le, "LABEL", {
        for: !0,
        class: !0,
        "data-svelte-h": !0
      }), Y(o) !== "svelte-1p9d3fm" && (o.textContent = c), u = R(le), h = b(le, "INPUT", {
        type: !0,
        id: !0,
        placeholder: !0,
        autocomplete: !0,
        class: !0
      }), le.forEach(E), d = R(se), _ = b(se, "DIV", { class: !0 });
      var X = I(_);
      p = b(X, "LABEL", {
        for: !0,
        class: !0,
        "data-svelte-h": !0
      }), Y(p) !== "svelte-pepa0a" && (p.textContent = v), w = R(X), S = b(X, "INPUT", {
        type: !0,
        id: !0,
        placeholder: !0,
        autocomplete: !0,
        class: !0
      }), X.forEach(E), A = R(se), y = b(se, "BUTTON", { type: !0, class: !0 });
      var ce = I(y);
      C = P(ce, O), ce.forEach(E), se.forEach(E), U.forEach(E), this.h();
    },
    h() {
      g(t, "class", "svelte-s1y7y7"), g(o, "for", "email"), g(o, "class", "svelte-s1y7y7"), g(h, "type", "email"), g(h, "id", "email"), g(h, "placeholder", "Email address"), g(h, "autocomplete", "email"), h.disabled = /*loading*/
      r[3], g(h, "class", "svelte-s1y7y7"), g(l, "class", "form-group svelte-s1y7y7"), g(p, "for", "password"), g(p, "class", "svelte-s1y7y7"), g(S, "type", "password"), g(S, "id", "password"), g(S, "placeholder", "Password"), g(S, "autocomplete", "current-password"), S.disabled = /*loading*/
      r[3], g(S, "class", "svelte-s1y7y7"), g(_, "class", "form-group svelte-s1y7y7"), g(y, "type", "submit"), g(y, "class", "button primary-button svelte-s1y7y7"), y.disabled = /*loading*/
      r[3], g(e, "class", "login-form svelte-s1y7y7");
    },
    m(W, U) {
      L(W, e, U), f(e, t), f(e, n), V && V.m(e, null), f(e, i), f(e, a), f(a, l), f(l, o), f(l, u), f(l, h), Ie(
        h,
        /*email*/
        r[0]
      ), f(a, d), f(a, _), f(_, p), f(_, w), f(_, S), Ie(
        S,
        /*password*/
        r[1]
      ), f(a, A), f(a, y), f(y, C), D || (F = [
        re(
          h,
          "input",
          /*input0_input_handler*/
          r[9]
        ),
        re(
          S,
          "input",
          /*input1_input_handler*/
          r[10]
        ),
        re(a, "submit", ir(
          /*handleSubmit*/
          r[4]
        ))
      ], D = !0);
    },
    p(W, [U]) {
      /*formError*/
      W[2] ? V ? V.p(W, U) : (V = Zs(W), V.c(), V.m(e, i)) : V && (V.d(1), V = null), U & /*loading*/
      8 && (h.disabled = /*loading*/
      W[3]), U & /*email*/
      1 && h.value !== /*email*/
      W[0] && Ie(
        h,
        /*email*/
        W[0]
      ), U & /*loading*/
      8 && (S.disabled = /*loading*/
      W[3]), U & /*password*/
      2 && S.value !== /*password*/
      W[1] && Ie(
        S,
        /*password*/
        W[1]
      ), U & /*loading*/
      8 && O !== (O = /*loading*/
      W[3] ? "Signing in..." : "Sign In") && M(C, O), U & /*loading*/
      8 && (y.disabled = /*loading*/
      W[3]);
    },
    i: q,
    o: q,
    d(W) {
      W && E(e), V && V.d(), D = !1, ve(F);
    }
  };
}
function xa(r, e, t) {
  let s, n, i, a;
  Pe(r, $r, (p) => t(7, i = p)), Pe(r, hs, (p) => t(8, a = p));
  let { onSuccess: l = () => {
  } } = e, o = "", c = "", u = "";
  async function h() {
    if (!o) {
      t(2, u = "Email is required");
      return;
    }
    if (!c) {
      t(2, u = "Password is required");
      return;
    }
    t(2, u = "");
    const p = await we.signIn(o, c);
    p.success ? (console.log("Login successful"), l()) : t(2, u = p.message || "Login failed");
  }
  function d() {
    o = this.value, t(0, o);
  }
  function _() {
    c = this.value, t(1, c);
  }
  return r.$$set = (p) => {
    "onSuccess" in p && t(5, l = p.onSuccess);
  }, r.$$.update = () => {
    r.$$.dirty & /*$isLoading*/
    256 && t(3, s = a), r.$$.dirty & /*$authError*/
    128 && t(6, n = i), r.$$.dirty & /*error*/
    64 && n && (t(2, u = n), we.clearError());
  }, [
    o,
    c,
    u,
    s,
    h,
    l,
    n,
    i,
    a,
    d,
    _
  ];
}
class Ja extends be {
  constructor(e) {
    super(), me(this, e, xa, za, ge, { onSuccess: 5 });
  }
}
function er(r) {
  let e, t;
  return {
    c() {
      e = m("div"), t = k(
        /*formError*/
        r[3]
      ), this.h();
    },
    l(s) {
      e = b(s, "DIV", { class: !0 });
      var n = I(e);
      t = P(
        n,
        /*formError*/
        r[3]
      ), n.forEach(E), this.h();
    },
    h() {
      g(e, "class", "error-message svelte-10vbupl");
    },
    m(s, n) {
      L(s, e, n), f(e, t);
    },
    p(s, n) {
      n & /*formError*/
      8 && M(
        t,
        /*formError*/
        s[3]
      );
    },
    d(s) {
      s && E(e);
    }
  };
}
function tr(r) {
  let e, t;
  return {
    c() {
      e = m("div"), t = k(
        /*successMessage*/
        r[4]
      ), this.h();
    },
    l(s) {
      e = b(s, "DIV", { class: !0 });
      var n = I(e);
      t = P(
        n,
        /*successMessage*/
        r[4]
      ), n.forEach(E), this.h();
    },
    h() {
      g(e, "class", "success-message svelte-10vbupl");
    },
    m(s, n) {
      L(s, e, n), f(e, t);
    },
    p(s, n) {
      n & /*successMessage*/
      16 && M(
        t,
        /*successMessage*/
        s[4]
      );
    },
    d(s) {
      s && E(e);
    }
  };
}
function Ka(r) {
  let e, t, s = "Create Account", n, i, a, l, o, c, u = "Email", h, d, _, p, v, w, S = "Password", A, y, O, C, D, F, V = "Confirm Password", W, U, se, le, X, ce = (
    /*loading*/
    r[5] ? "Creating account..." : "Create Account"
  ), Q, ne, Z, pe, H = (
    /*formError*/
    r[3] && er(r)
  ), K = (
    /*successMessage*/
    r[4] && tr(r)
  );
  return {
    c() {
      e = m("div"), t = m("h2"), t.textContent = s, n = T(), H && H.c(), i = T(), K && K.c(), a = T(), l = m("form"), o = m("div"), c = m("label"), c.textContent = u, h = T(), d = m("input"), p = T(), v = m("div"), w = m("label"), w.textContent = S, A = T(), y = m("input"), C = T(), D = m("div"), F = m("label"), F.textContent = V, W = T(), U = m("input"), le = T(), X = m("button"), Q = k(ce), this.h();
    },
    l($) {
      e = b($, "DIV", { class: !0 });
      var j = I(e);
      t = b(j, "H2", { class: !0, "data-svelte-h": !0 }), Y(t) !== "svelte-lqaecl" && (t.textContent = s), n = R(j), H && H.l(j), i = R(j), K && K.l(j), a = R(j), l = b(j, "FORM", {});
      var z = I(l);
      o = b(z, "DIV", { class: !0 });
      var ie = I(o);
      c = b(ie, "LABEL", {
        for: !0,
        class: !0,
        "data-svelte-h": !0
      }), Y(c) !== "svelte-dprrif" && (c.textContent = u), h = R(ie), d = b(ie, "INPUT", {
        type: !0,
        id: !0,
        placeholder: !0,
        autocomplete: !0,
        class: !0
      }), ie.forEach(E), p = R(z), v = b(z, "DIV", { class: !0 });
      var te = I(v);
      w = b(te, "LABEL", {
        for: !0,
        class: !0,
        "data-svelte-h": !0
      }), Y(w) !== "svelte-1y770v" && (w.textContent = S), A = R(te), y = b(te, "INPUT", {
        type: !0,
        id: !0,
        placeholder: !0,
        autocomplete: !0,
        class: !0
      }), te.forEach(E), C = R(z), D = b(z, "DIV", { class: !0 });
      var B = I(D);
      F = b(B, "LABEL", {
        for: !0,
        class: !0,
        "data-svelte-h": !0
      }), Y(F) !== "svelte-1kqgfb9" && (F.textContent = V), W = R(B), U = b(B, "INPUT", {
        type: !0,
        id: !0,
        placeholder: !0,
        autocomplete: !0,
        class: !0
      }), B.forEach(E), le = R(z), X = b(z, "BUTTON", { type: !0, class: !0 });
      var x = I(X);
      Q = P(x, ce), x.forEach(E), z.forEach(E), j.forEach(E), this.h();
    },
    h() {
      g(t, "class", "svelte-10vbupl"), g(c, "for", "signup-email"), g(c, "class", "svelte-10vbupl"), g(d, "type", "email"), g(d, "id", "signup-email"), g(d, "placeholder", "Email address"), g(d, "autocomplete", "email"), d.disabled = _ = /*loading*/
      r[5] || !!/*successMessage*/
      r[4], g(d, "class", "svelte-10vbupl"), g(o, "class", "form-group svelte-10vbupl"), g(w, "for", "signup-password"), g(w, "class", "svelte-10vbupl"), g(y, "type", "password"), g(y, "id", "signup-password"), g(y, "placeholder", "Password (min 6 characters)"), g(y, "autocomplete", "new-password"), y.disabled = O = /*loading*/
      r[5] || !!/*successMessage*/
      r[4], g(y, "class", "svelte-10vbupl"), g(v, "class", "form-group svelte-10vbupl"), g(F, "for", "confirm-password"), g(F, "class", "svelte-10vbupl"), g(U, "type", "password"), g(U, "id", "confirm-password"), g(U, "placeholder", "Confirm password"), g(U, "autocomplete", "new-password"), U.disabled = se = /*loading*/
      r[5] || !!/*successMessage*/
      r[4], g(U, "class", "svelte-10vbupl"), g(D, "class", "form-group svelte-10vbupl"), g(X, "type", "submit"), g(X, "class", "button primary-button svelte-10vbupl"), X.disabled = ne = /*loading*/
      r[5] || !!/*successMessage*/
      r[4], g(e, "class", "signup-form svelte-10vbupl");
    },
    m($, j) {
      L($, e, j), f(e, t), f(e, n), H && H.m(e, null), f(e, i), K && K.m(e, null), f(e, a), f(e, l), f(l, o), f(o, c), f(o, h), f(o, d), Ie(
        d,
        /*email*/
        r[0]
      ), f(l, p), f(l, v), f(v, w), f(v, A), f(v, y), Ie(
        y,
        /*password*/
        r[1]
      ), f(l, C), f(l, D), f(D, F), f(D, W), f(D, U), Ie(
        U,
        /*confirmPassword*/
        r[2]
      ), f(l, le), f(l, X), f(X, Q), Z || (pe = [
        re(
          d,
          "input",
          /*input0_input_handler*/
          r[11]
        ),
        re(
          y,
          "input",
          /*input1_input_handler*/
          r[12]
        ),
        re(
          U,
          "input",
          /*input2_input_handler*/
          r[13]
        ),
        re(l, "submit", ir(
          /*handleSubmit*/
          r[6]
        ))
      ], Z = !0);
    },
    p($, [j]) {
      /*formError*/
      $[3] ? H ? H.p($, j) : (H = er($), H.c(), H.m(e, i)) : H && (H.d(1), H = null), /*successMessage*/
      $[4] ? K ? K.p($, j) : (K = tr($), K.c(), K.m(e, a)) : K && (K.d(1), K = null), j & /*loading, successMessage*/
      48 && _ !== (_ = /*loading*/
      $[5] || !!/*successMessage*/
      $[4]) && (d.disabled = _), j & /*email*/
      1 && d.value !== /*email*/
      $[0] && Ie(
        d,
        /*email*/
        $[0]
      ), j & /*loading, successMessage*/
      48 && O !== (O = /*loading*/
      $[5] || !!/*successMessage*/
      $[4]) && (y.disabled = O), j & /*password*/
      2 && y.value !== /*password*/
      $[1] && Ie(
        y,
        /*password*/
        $[1]
      ), j & /*loading, successMessage*/
      48 && se !== (se = /*loading*/
      $[5] || !!/*successMessage*/
      $[4]) && (U.disabled = se), j & /*confirmPassword*/
      4 && U.value !== /*confirmPassword*/
      $[2] && Ie(
        U,
        /*confirmPassword*/
        $[2]
      ), j & /*loading*/
      32 && ce !== (ce = /*loading*/
      $[5] ? "Creating account..." : "Create Account") && M(Q, ce), j & /*loading, successMessage*/
      48 && ne !== (ne = /*loading*/
      $[5] || !!/*successMessage*/
      $[4]) && (X.disabled = ne);
    },
    i: q,
    o: q,
    d($) {
      $ && E(e), H && H.d(), K && K.d(), Z = !1, ve(pe);
    }
  };
}
function Ya(r, e, t) {
  let s, n, i, a;
  Pe(r, $r, (S) => t(9, i = S)), Pe(r, hs, (S) => t(10, a = S));
  let { onSuccess: l = () => {
  } } = e, o = "", c = "", u = "", h = "", d = "";
  async function _() {
    if (t(3, h = ""), t(4, d = ""), !o) {
      t(3, h = "Email is required");
      return;
    }
    if (!c) {
      t(3, h = "Password is required");
      return;
    }
    if (c.length < 6) {
      t(3, h = "Password must be at least 6 characters");
      return;
    }
    if (c !== u) {
      t(3, h = "Passwords do not match");
      return;
    }
    t(3, h = "");
    const S = await we.signUp(o, c);
    S.success ? S.needsConfirmation ? t(4, d = "Please check your email for a confirmation link") : (console.log("Signup successful"), l()) : t(3, h = S.message || "Signup failed");
  }
  function p() {
    o = this.value, t(0, o);
  }
  function v() {
    c = this.value, t(1, c);
  }
  function w() {
    u = this.value, t(2, u);
  }
  return r.$$set = (S) => {
    "onSuccess" in S && t(7, l = S.onSuccess);
  }, r.$$.update = () => {
    r.$$.dirty & /*$isLoading*/
    1024 && t(5, s = a), r.$$.dirty & /*$authError*/
    512 && t(8, n = i), r.$$.dirty & /*error*/
    256 && n && (t(3, h = n), we.clearError());
  }, [
    o,
    c,
    u,
    h,
    d,
    s,
    _,
    l,
    n,
    i,
    a,
    p,
    v,
    w
  ];
}
class Xa extends be {
  constructor(e) {
    super(), me(this, e, Ya, Ka, ge, { onSuccess: 7 });
  }
}
function Qa(r) {
  let e, t;
  return e = new Xa({ props: { onSuccess: (
    /*func*/
    r[8]
  ) } }), {
    c() {
      pt(e.$$.fragment);
    },
    l(s) {
      Et(e.$$.fragment, s);
    },
    m(s, n) {
      nt(e, s, n), t = !0;
    },
    p: q,
    i(s) {
      t || (J(e.$$.fragment, s), t = !0);
    },
    o(s) {
      ae(e.$$.fragment, s), t = !1;
    },
    d(s) {
      it(e, s);
    }
  };
}
function Za(r) {
  let e, t;
  return e = new Ja({
    props: { onSuccess: (
      /*handleAuthSuccess*/
      r[1]
    ) }
  }), {
    c() {
      pt(e.$$.fragment);
    },
    l(s) {
      Et(e.$$.fragment, s);
    },
    m(s, n) {
      nt(e, s, n), t = !0;
    },
    p: q,
    i(s) {
      t || (J(e.$$.fragment, s), t = !0);
    },
    o(s) {
      ae(e.$$.fragment, s), t = !1;
    },
    d(s) {
      it(e, s);
    }
  };
}
function eo(r) {
  let e, t, s, n, i, a, l, o, c, u, h, d, _, p, v, w;
  const S = [Za, Qa], A = [];
  function y(O, C) {
    return (
      /*activeTab*/
      O[0] === "login" ? 0 : 1
    );
  }
  return d = y(r), _ = A[d] = S[d](r), {
    c() {
      e = m("div"), t = m("div"), s = m("button"), n = k("Sign In"), a = T(), l = m("button"), o = k("Create Account"), u = T(), h = m("div"), _.c(), this.h();
    },
    l(O) {
      e = b(O, "DIV", { class: !0 });
      var C = I(e);
      t = b(C, "DIV", { class: !0 });
      var D = I(t);
      s = b(D, "BUTTON", { class: !0 });
      var F = I(s);
      n = P(F, "Sign In"), F.forEach(E), a = R(D), l = b(D, "BUTTON", { class: !0 });
      var V = I(l);
      o = P(V, "Create Account"), V.forEach(E), D.forEach(E), u = R(C), h = b(C, "DIV", { class: !0 });
      var W = I(h);
      _.l(W), W.forEach(E), C.forEach(E), this.h();
    },
    h() {
      g(s, "class", i = "tab-button " + /*activeTab*/
      (r[0] === "login" ? "active" : "") + " svelte-1vnb611"), g(l, "class", c = "tab-button " + /*activeTab*/
      (r[0] === "signup" ? "active" : "") + " svelte-1vnb611"), g(t, "class", "auth-tabs svelte-1vnb611"), g(h, "class", "auth-content svelte-1vnb611"), g(e, "class", "auth-container svelte-1vnb611");
    },
    m(O, C) {
      L(O, e, C), f(e, t), f(t, s), f(s, n), f(t, a), f(t, l), f(l, o), f(e, u), f(e, h), A[d].m(h, null), p = !0, v || (w = [
        re(
          s,
          "click",
          /*click_handler*/
          r[6]
        ),
        re(
          l,
          "click",
          /*click_handler_1*/
          r[7]
        )
      ], v = !0);
    },
    p(O, [C]) {
      (!p || C & /*activeTab*/
      1 && i !== (i = "tab-button " + /*activeTab*/
      (O[0] === "login" ? "active" : "") + " svelte-1vnb611")) && g(s, "class", i), (!p || C & /*activeTab*/
      1 && c !== (c = "tab-button " + /*activeTab*/
      (O[0] === "signup" ? "active" : "") + " svelte-1vnb611")) && g(l, "class", c);
      let D = d;
      d = y(O), d === D ? A[d].p(O, C) : (Ue(), ae(A[D], 1, 1, () => {
        A[D] = null;
      }), Ve(), _ = A[d], _ ? _.p(O, C) : (_ = A[d] = S[d](O), _.c()), J(_, 1), _.m(h, null));
    },
    i(O) {
      p || (J(_), p = !0);
    },
    o(O) {
      ae(_), p = !1;
    },
    d(O) {
      O && E(e), A[d].d(), v = !1, ve(w);
    }
  };
}
function to(r, e, t) {
  let s;
  Pe(r, Hr, (d) => t(5, s = d));
  let { redirectUrl: n = "/" } = e, { showSignup: i = !1 } = e, a = i ? "signup" : "login";
  De(() => {
    we.init();
  });
  function l() {
    let d = n || "/";
    d.endsWith("/") && d !== "/" && (d = d.slice(0, -1)), window.location.href = d;
  }
  function o(d) {
    t(0, a = d);
  }
  const c = () => o("login"), u = () => o("signup"), h = () => o("login");
  return r.$$set = (d) => {
    "redirectUrl" in d && t(3, n = d.redirectUrl), "showSignup" in d && t(4, i = d.showSignup);
  }, r.$$.update = () => {
    r.$$.dirty & /*$isAuthenticated*/
    32 && s && l();
  }, [
    a,
    l,
    o,
    n,
    i,
    s,
    c,
    u,
    h
  ];
}
class Br extends be {
  constructor(e) {
    super(), me(this, e, to, eo, ge, { redirectUrl: 3, showSignup: 4 });
  }
}
const { window: so } = Jr;
function ro(r) {
  let e, t = "Sign In", s, n;
  return {
    c() {
      e = m("button"), e.textContent = t, this.h();
    },
    l(i) {
      e = b(i, "BUTTON", { class: !0, "data-svelte-h": !0 }), Y(e) !== "svelte-15d6po7" && (e.textContent = t), this.h();
    },
    h() {
      g(e, "class", "sign-in-button svelte-yh60l2");
    },
    m(i, a) {
      L(i, e, a), s || (n = re(e, "click", oo), s = !0);
    },
    p: q,
    d(i) {
      i && E(e), s = !1, n();
    }
  };
}
function no(r) {
  var u, h;
  let e, t, s = (
    /*$user*/
    (((h = (u = r[3].email) == null ? void 0 : u[0]) == null ? void 0 : h.toUpperCase()) || "U") + ""
  ), n, i, a, l, o, c = (
    /*dropdownOpen*/
    r[0] && sr(r)
  );
  return {
    c() {
      e = m("button"), t = m("div"), n = k(s), i = T(), c && c.c(), a = Le(), this.h();
    },
    l(d) {
      e = b(d, "BUTTON", { class: !0 });
      var _ = I(e);
      t = b(_, "DIV", { class: !0 });
      var p = I(t);
      n = P(p, s), p.forEach(E), _.forEach(E), i = R(d), c && c.l(d), a = Le(), this.h();
    },
    h() {
      g(t, "class", "user-avatar svelte-yh60l2"), g(e, "class", "user-button svelte-yh60l2");
    },
    m(d, _) {
      L(d, e, _), f(e, t), f(t, n), L(d, i, _), c && c.m(d, _), L(d, a, _), l || (o = re(
        e,
        "click",
        /*toggleDropdown*/
        r[4]
      ), l = !0);
    },
    p(d, _) {
      var p, v;
      _ & /*$user*/
      8 && s !== (s = /*$user*/
      (((v = (p = d[3].email) == null ? void 0 : p[0]) == null ? void 0 : v.toUpperCase()) || "U") + "") && M(n, s), /*dropdownOpen*/
      d[0] ? c ? c.p(d, _) : (c = sr(d), c.c(), c.m(a.parentNode, a)) : c && (c.d(1), c = null);
    },
    d(d) {
      d && (E(e), E(i), E(a)), c && c.d(d), l = !1, o();
    }
  };
}
function io(r) {
  let e, t = '<span class="loading-dot svelte-yh60l2"></span> <span class="loading-dot svelte-yh60l2"></span> <span class="loading-dot svelte-yh60l2"></span>';
  return {
    c() {
      e = m("div"), e.innerHTML = t, this.h();
    },
    l(s) {
      e = b(s, "DIV", { class: !0, "data-svelte-h": !0 }), Y(e) !== "svelte-1fyc92b" && (e.innerHTML = t), this.h();
    },
    h() {
      g(e, "class", "loading-indicator svelte-yh60l2");
    },
    m(s, n) {
      L(s, e, n);
    },
    p: q,
    d(s) {
      s && E(e);
    }
  };
}
function sr(r) {
  let e, t, s, n = (
    /*$user*/
    r[3].email + ""
  ), i, a, l, o, c, u = "My Profile", h, d, _ = "Sign Out", p, v;
  return {
    c() {
      e = m("div"), t = m("div"), s = m("span"), i = k(n), a = T(), l = m("div"), o = T(), c = m("button"), c.textContent = u, h = T(), d = m("button"), d.textContent = _, this.h();
    },
    l(w) {
      e = b(w, "DIV", { class: !0 });
      var S = I(e);
      t = b(S, "DIV", { class: !0 });
      var A = I(t);
      s = b(A, "SPAN", { class: !0 });
      var y = I(s);
      i = P(y, n), y.forEach(E), A.forEach(E), a = R(S), l = b(S, "DIV", { class: !0 }), I(l).forEach(E), o = R(S), c = b(S, "BUTTON", { class: !0, "data-svelte-h": !0 }), Y(c) !== "svelte-1apszzx" && (c.textContent = u), h = R(S), d = b(S, "BUTTON", { class: !0, "data-svelte-h": !0 }), Y(d) !== "svelte-1c7nt7f" && (d.textContent = _), S.forEach(E), this.h();
    },
    h() {
      g(s, "class", "user-email svelte-yh60l2"), g(t, "class", "user-info svelte-yh60l2"), g(l, "class", "dropdown-divider svelte-yh60l2"), g(c, "class", "dropdown-item svelte-yh60l2"), g(d, "class", "dropdown-item svelte-yh60l2"), g(e, "class", "dropdown-menu svelte-yh60l2");
    },
    m(w, S) {
      L(w, e, S), f(e, t), f(t, s), f(s, i), f(e, a), f(e, l), f(e, o), f(e, c), f(e, h), f(e, d), p || (v = [
        re(
          c,
          "click",
          /*click_handler*/
          r[7]
        ),
        re(
          d,
          "click",
          /*handleLogout*/
          r[6]
        )
      ], p = !0);
    },
    p(w, S) {
      S & /*$user*/
      8 && n !== (n = /*$user*/
      w[3].email + "") && M(i, n);
    },
    d(w) {
      w && E(e), p = !1, ve(v);
    }
  };
}
function ao(r) {
  let e, t, s;
  function n(l, o) {
    return (
      /*$isLoading*/
      l[1] ? io : (
        /*$isAuthenticated*/
        l[2] && /*$user*/
        l[3] ? no : ro
      )
    );
  }
  let i = n(r), a = i(r);
  return {
    c() {
      e = m("div"), a.c(), this.h();
    },
    l(l) {
      e = b(l, "DIV", { class: !0 });
      var o = I(e);
      a.l(o), o.forEach(E), this.h();
    },
    h() {
      g(e, "class", "user-status svelte-yh60l2");
    },
    m(l, o) {
      L(l, e, o), a.m(e, null), t || (s = re(
        so,
        "click",
        /*handleClickOutside*/
        r[5]
      ), t = !0);
    },
    p(l, [o]) {
      i === (i = n(l)) && a ? a.p(l, o) : (a.d(1), a = i(l), a && (a.c(), a.m(e, null)));
    },
    i: q,
    o: q,
    d(l) {
      l && E(e), a.d(), t = !1, s();
    }
  };
}
function oo() {
  window.location.href = "/auth";
}
function lo(r, e, t) {
  let s, n, i;
  Pe(r, hs, (h) => t(1, s = h)), Pe(r, Hr, (h) => t(2, n = h)), Pe(r, qa, (h) => t(3, i = h));
  let a = !1;
  De(() => {
    we.init();
  });
  function l() {
    t(0, a = !a);
  }
  function o(h) {
    h.target.closest(".user-status") || t(0, a = !1);
  }
  De(() => (document.addEventListener("click", o), () => {
    document.removeEventListener("click", o);
  }));
  async function c() {
    (await we.signOut()).success && (window.location.href = "/");
  }
  return [
    a,
    s,
    n,
    i,
    l,
    o,
    c,
    () => {
      try {
        fetch("/auth/profile", { method: "HEAD" }).then((h) => {
          h.ok && (window.location.href = "/auth/profile");
        });
      } catch {
        window.location.href = "/auth/profile";
      }
    }
  ];
}
class Gr extends be {
  constructor(e) {
    super(), me(this, e, lo, ao, ge, {});
  }
}
const co = {
  minilemma: (r, e) => new kt({ target: r, props: e }),
  minisentence: (r, e) => new cr({ target: r, props: e }),
  miniwordform: (r, e) => new is({ target: r, props: e }),
  miniwordformlist: (r, e) => new ur({ target: r, props: e }),
  miniphrase: (r, e) => new hr({ target: r, props: e }),
  sentence: (r, e) => new dr({ target: r, props: e }),
  flashcardapp: (r, e) => new fr({ target: r, props: e }),
  flashcardlanding: (r, e) => new _r({ target: r, props: e }),
  auth: (r, e) => new Br({ target: r, props: e }),
  userstatus: (r, e) => new Gr({ target: r, props: e })
};
typeof window < "u" && (window.HzComponents = {
  components: co,
  MiniLemma: kt,
  MiniSentence: cr,
  MiniWordform: is,
  MiniWordformList: ur,
  MiniPhrase: hr,
  Sentence: dr,
  FlashcardApp: fr,
  FlashcardLanding: _r,
  AuthPage: Br,
  UserStatus: Gr
});
export {
  Br as A,
  fr as F,
  kt as M,
  dr as S,
  Gr as U,
  _r as a,
  hr as b,
  cr as c,
  is as d,
  ur as e,
  co as f,
  ho as g
};
//# sourceMappingURL=index-VAzTizur.js.map
