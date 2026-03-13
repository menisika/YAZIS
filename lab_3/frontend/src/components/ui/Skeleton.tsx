interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  style?: React.CSSProperties;
}

export function Skeleton({ width = "100%", height = 16, style }: SkeletonProps) {
  return (
    <div
      className="skeleton"
      style={{ width, height, ...style }}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="card" style={{ padding: 16 }}>
      <Skeleton height={20} width="60%" style={{ marginBottom: 10 }} />
      <Skeleton height={14} width="40%" style={{ marginBottom: 8 }} />
      <Skeleton height={14} width="80%" />
    </div>
  );
}
