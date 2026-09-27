const API_URL = ''

async function readResponse(response, fallbackMessage) {
  const responseText = await response.text()
  let data

  if (responseText) {
    try {
      data = JSON.parse(responseText)
    } catch {
      if (response.ok) {
        throw new Error(`The server returned an invalid response (HTTP ${response.status}).`)
      }
    }
  }

  if (!response.ok) {
    const detail = data?.detail
    const message = typeof detail === 'string'
      ? detail
      : detail
        ? JSON.stringify(detail)
        : `${fallbackMessage} (HTTP ${response.status}).`
    throw new Error(message)
  }

  if (data === undefined) {
    throw new Error(`The server returned an empty response (HTTP ${response.status}).`)
  }

  return data
}

export async function uploadCsv(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  })

  return readResponse(response, 'Could not upload CSV.')
}

export async function getAnalysis() {
  const response = await fetch(`${API_URL}/api/analyze`)
  return readResponse(response, 'Could not analyze transactions.')
}

export async function getProfiles() {
  const response = await fetch(`${API_URL}/api/profiles`)
  return readResponse(response, 'Could not load profile data.')
}

export async function getReview() {
  const response = await fetch(`${API_URL}/api/review`)
  return readResponse(response, 'Could not load review cases.')
}

export async function getExportReport() {
  const response = await fetch(`${API_URL}/api/export`)
  return readResponse(response, 'Could not export the report.')
}

export async function calculateTax(payload) {
  const response = await fetch(`${API_URL}/api/tax/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  return readResponse(response, 'Could not calculate tax.')
}
