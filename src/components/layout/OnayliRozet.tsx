/** NSosyal'in mavi onaylı hesap rozeti */
export function OnayliRozet({ boyut = 16 }: { boyut?: number }) {
  return (
    <svg
      width={boyut}
      height={boyut}
      viewBox="0 0 24 24"
      className="shrink-0"
      role="img"
      aria-label="Onaylı hesap"
    >
      <path
        fill="var(--color-onayli)"
        d="M12 1.5 15 0l2.2 2.6 3.4.3.3 3.4L23.5 8.5 22 12l1.5 3.5-2.6 2.2-.3 3.4-3.4.3L15 24l-3-1.5L9 24l-2.2-2.6-3.4-.3-.3-3.4L.5 15.5 2 12 .5 8.5l2.6-2.2.3-3.4 3.4-.3L9 0z"
      />
      <path
        fill="#fff"
        d="M10.6 16.2 6.8 12.4l1.6-1.6 2.2 2.2 5-5 1.6 1.6z"
      />
    </svg>
  );
}
