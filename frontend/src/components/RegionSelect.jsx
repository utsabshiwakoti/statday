import { REGIONS } from '../regions'

export default function RegionSelect({ value, onChange, label = 'Region' }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} aria-label={label} className="region-select">
      {REGIONS.map(([code, name]) => (
        <option key={code} value={code}>{name}</option>
      ))}
    </select>
  )
}
