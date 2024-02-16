const baseUrl = 'https://sync-calendar-app-xt6u7vzbeq-de.a.run.app'
// const baseUrl = 'http://localhost:8080'

function isLoggedIn () {
  if (document.getElementsByClassName('login').length === 0 && window.location.href !== 'https://moodle.ncku.edu.tw/login/index.php') {
    return true
  } else {
    return false
  }
}

function getCookie (name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
}

function getAuthUrl () {
  return fetch(baseUrl + '/auth', {
    method: 'POST',
    credentials: 'include',
    redirect: 'manual'
  }).then((response) => {
    return response.text()
  }).catch((error) => {
    console.error(error)
    return null
  })
}

async function auth () {
  const authUrl = await getAuthUrl()
  if (authUrl === null) {
    return false
  } else {
    window.open(authUrl)
    return true
  }
}

function login () {
  return fetch(baseUrl + '/login', {
    method: 'POST',
    headers: {
      'Moodle-Session': getCookie('MoodleSession')
    },
    credentials: 'include'
  }).then((response) => {
    return null
  }).catch((error) => {
    console.error(error)
    return null
  })
}

function sync () {
  if (isLoggedIn()) {
    return fetch(baseUrl + '/sync', {
      method: 'POST',
      credentials: 'include'
    }).then((response) => {
      return response
    }).catch((error) => {
      console.error(error)
      return null
    })
  } else {
    return 'Not logged in'
  }
}

function onGetEmail () {
  return fetch(baseUrl + '/binded-email', {
    method: 'GET',
    credentials: 'include'
  }).then((response) => {
    if (response.ok) {
      return response.text()
    } else {
      return null
    }
  }).catch((error) => {
    console.error(error)
    return null
  })
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'sync') {
    sync().then(response => {
      if (response === null) {
        sendResponse({ status: 'error' })
      } else {
        sendResponse({ status: response.ok ? 'ok' : 'error' })
      }
    })
    return true
  } else if (request.action === 'auth') {
    auth().then(openedTab => {
      sendResponse({ status: openedTab ? 'ok' : 'error' })
    })
    return true
  } else if (request.action === 'isLoggedIn') {
    if (isLoggedIn()) {
      login().then(() => {
        sendResponse({ loggedIn: isLoggedIn() })
      }).catch((error) => {
        console.error(error)
        sendResponse({ loggedIn: false })
      })
    } else {
      sendResponse({ loggedIn: false })
    }
    return true
  } else if (request.action === 'getEmail') {
    onGetEmail().then(email => {
      sendResponse({ email })
    })
    return true
  }
})
