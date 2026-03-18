import { ref } from 'vue'

function getCsrfToken() {
  const match = document.cookie.match(/csrf_token=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : ''
}

async function handleResponse(res) {
  if (res.status === 403 || res.status === 401) {
    window.location.href = '/login?redirect-to=/portal/'
    throw new Error('Session expired')
  }
  const data = await res.json()
  if (data.exc) {
    const msg = typeof data.exc === 'string' ? data.exc : JSON.stringify(data.exc)
    throw new Error(data._server_messages || msg)
  }
  return data.message
}

export function useFrappe() {
  const loading = ref(false)
  const error = ref(null)

  async function call(method, params = {}, options = {}) {
    loading.value = true
    error.value = null
    try {
      let url = `/api/method/${method}`
      const fetchOptions = {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': getCsrfToken(),
        },
      }
      if (options.method === 'GET') {
        const qs = new URLSearchParams(params).toString()
        if (qs) url += `?${qs}`
        fetchOptions.method = 'GET'
      } else {
        fetchOptions.method = 'POST'
        fetchOptions.body = JSON.stringify(params)
      }
      const res = await fetch(url, fetchOptions)
      return await handleResponse(res)
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function getList(doctype, { fields, filters, orderBy, start, pageLength } = {}) {
    return call('frappe.client.get_list', {
      doctype,
      fields: fields || ['name'],
      filters: filters || {},
      order_by: orderBy || 'modified desc',
      start: start || 0,
      page_length: pageLength || 20,
    }, { method: 'GET' })
  }

  return { call, getList, loading, error }
}
