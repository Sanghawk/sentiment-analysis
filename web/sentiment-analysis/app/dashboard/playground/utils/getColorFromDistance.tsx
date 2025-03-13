export function getBorderColorFromDistance(distance: number) {
  if (distance < 0.3) return "border-green-500";
  if (distance < 0.4) return "border-lime-500";
  if (distance < 0.5) return "border-yellow-500";
  if (distance < 0.6) return "border-amber-500";
  if (distance < 0.7) return "border-orange-500";
  return "border-red-500";
}
export function getUnderlineColorFromDistance(distance: number) {
  if (distance < 0.3) return "decoration-green-500";
  if (distance < 0.4) return "decoration-lime-500";
  if (distance < 0.5) return "decoration-yellow-500";
  if (distance < 0.6) return "decoration-amber-500";
  if (distance < 0.7) return "decoration-orange-500";
  return "decoration-red-500";
}
