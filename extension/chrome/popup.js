// Popup script for the Chrome extension

// Define the initial state
let state = {
  loggedIn: false,
  googleAcc: null,
  errorMsg: null,
  loading: false,
  success: false
}

function setLoadingState () {
  state.loading = true
  state.errorMsg = null
  state.success = false
}

async function onSyncClick () {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
  const response = await chrome.tabs.sendMessage(tab.id, { action: 'sync' })
  state.loading = false
  if (response.status === 'ok') {
    state.success = true
  } else {
    state.errorMsg = '同步失敗，請稍後再試'
  }
  renderButtons()
}

async function onAuthClick () {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
  const response = await chrome.tabs.sendMessage(tab.id, { action: 'auth' })
  state.loading = false
  if (response.status !== 'ok') {
    state.errorMsg = '綁定失敗，請稍後再試'
  }
  renderButtons()
}

function setLocalEmail (email) {
  chrome.storage.sync.set({ email }, function () {
  })
}

async function loadLocalEmail () {
  const readLocalEmail = async () => {
    return new Promise((resolve, reject) => {
      chrome.storage.sync.get('email', function (result) {
        resolve(result.email)
      })
    })
  }
  const email = await readLocalEmail()
  state.googleAcc = email
}

async function onGetEmail () {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
  const response = await chrome.tabs.sendMessage(tab.id, { action: 'getEmail' })
  state.googleAcc = response.email
  if (response.email !== null) {
    setLocalEmail(response.email)
  }
}

function renderButtons () {
  const container = document.getElementById('button-container')
  container.innerHTML = ''
  let syncButton
  if (state.loggedIn === false) {
    syncButton = createSyncButton(false, '請先登入moodle')
    container.appendChild(syncButton)
    return
  } else if (state.googleAcc === null || state.googleAcc === '') {
    syncButton = createSyncButton(false, '請先綁定帳號')
  } else if (state.errorMsg !== null) {
    syncButton = createSyncButton(true, state.errorMsg)
  } else {
    syncButton = createSyncButton(true, null, state.loading, state.success)
  }
  const bindButton = createBindAccountButton(false)

  container.appendChild(syncButton)
  container.appendChild(bindButton)
  container.appendChild(createText('目前帳號:', 'info'))
  container.appendChild(createText(state.googleAcc, 'info'))
}

function createLoader () {
  const loader = document.createElement('span')
  loader.classList.add('loader')
  return loader
}

function createSuccessCheck () {
  const check = document.createElement('img')
  check.src = 'ui/images/check.png'
  check.classList.add('check')
  return check
}

function createText (text, type, active = true) {
  const textClass = 'text-' + type
  const newSpan = document.createElement('span')
  newSpan.textContent = text
  newSpan.classList.add(textClass)
  if (type === 'info') {
    newSpan.classList.add('center')
  }
  if (active === false) {
    newSpan.classList.add('disabled')
  }
  return newSpan
}

function createGoogleIcon (primary = false) {
  const newIcon = document.createElement('img')
  newIcon.src = 'ui/images/google_icon.png'
  if (primary) {
    newIcon.classList.add('google-icon-primary')
  } else {
    newIcon.classList.add('google-icon-secondary')
  }
  return newIcon
}

function createBindAccountButton (primary = false) {
  const button = document.createElement('button')
  button.appendChild(createGoogleIcon(true))
  if (primary) {
    button.classList.add('center', 'btn-primary', 'btn')
    button.appendChild(createText('綁定帳號', 'primary'))
  } else {
    button.classList.add('center', 'btn-secondary', 'btn')
    button.appendChild(createText('切換帳號', 'secondary'))
  }
  button.addEventListener('click', () => {
    setLoadingState()
    onAuthClick()
    onGetEmail()
    renderButtons()
  })
  return button
}

function createSyncButton (active = true, errorMsg = null, loading = false, success = false) {
  const button = document.createElement('button')

  if (loading || active === false) {
    button.classList.add('center', 'btn-primary', 'btn', 'disabled')
    button.appendChild(createText('同步', 'primary', false))
    if (loading) {
      button.appendChild(createLoader())
    }
  } else {
    button.classList.add('center', 'btn-primary', 'btn')
    button.appendChild(createText('同步', 'primary'))
    if (success) {
      button.appendChild(createSuccessCheck())
    }
    button.addEventListener('click', () => {
      setLoadingState()
      onSyncClick()
      renderButtons()
    })
  }

  if (errorMsg !== null) {
    button.classList.add('error')
    button.appendChild(createText(errorMsg, 'error'))
  }
  return button
}

async function init () {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
  const loginResponse = await chrome.tabs.sendMessage(tab.id, { action: 'isLoggedIn' })
  state.loggedIn = loginResponse.loggedIn

  await loadLocalEmail()
  if (state.googleAcc === null || state.googleAcc === '' || state.googleAcc === undefined) {
    await onGetEmail()
  } else if (state.loggedIn) {
    renderButtons()
    await onGetEmail()
  }
  renderButtons()
}

init()
