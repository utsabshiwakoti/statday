// Region codes for the pickers, kept here rather than fetched so the pickers render immediately.
// They match /v1/regions, which is the source of truth.
export const REGIONS = [
  ['AB', 'Alberta'], ['BC', 'British Columbia'], ['MB', 'Manitoba'], ['NB', 'New Brunswick'],
  ['NL', 'Newfoundland and Labrador'], ['NS', 'Nova Scotia'], ['ON', 'Ontario'], ['PE', 'Prince Edward Island'],
  ['QC', 'Quebec'], ['SK', 'Saskatchewan'], ['NT', 'Northwest Territories'], ['NU', 'Nunavut'], ['YT', 'Yukon'],
  ['CA', 'Federal (Canada Labour Code)'],
]

// A sensible default region from the browser's time zone. Only a guess; the picker changes it.
const BY_ZONE = {
  'America/Vancouver': 'BC', 'America/Edmonton': 'AB', 'America/Regina': 'SK', 'America/Winnipeg': 'MB',
  'America/Toronto': 'ON', 'America/Montreal': 'QC', 'America/Moncton': 'NB', 'America/Halifax': 'NS',
  'America/St_Johns': 'NL', 'America/Whitehorse': 'YT', 'America/Yellowknife': 'NT', 'America/Iqaluit': 'NU',
}

export function guessRegion() {
  return BY_ZONE[Intl.DateTimeFormat().resolvedOptions().timeZone] || 'ON'
}
