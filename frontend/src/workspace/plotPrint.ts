import type uPlot from "uplot";

// Snapshot the existing plot at paper-readable width. Native printing can
// snapshot before ResizeObserver runs; an image fits paper without cropping
// the canvas or inventing another data renderer.
export function installPlotPrint(
  plot: uPlot,
  target: HTMLElement,
  image: HTMLImageElement,
  height: number,
) {
  const prepare = () => {
    plot.batch(() => plot.setSize({ width: 640, height }));
    image.src = plot.ctx.canvas.toDataURL("image/png");
  };
  const restore = () =>
    plot.setSize({ width: Math.max(1, target.clientWidth), height });
  window.addEventListener("beforeprint", prepare);
  window.addEventListener("afterprint", restore);
  return () => {
    window.removeEventListener("beforeprint", prepare);
    window.removeEventListener("afterprint", restore);
  };
}
