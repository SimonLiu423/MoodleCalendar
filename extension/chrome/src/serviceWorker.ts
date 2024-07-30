import { API_URL, MOODLE_URL } from './constants';
import axios from 'axios';

async function getMoodleSession(): Promise<string | undefined> {
  const cookie = await chrome.cookies.get({
    url: 'https://moodle.ncku.edu.tw/',
    name: 'MoodleSession',
  });
  return cookie?.value;
}

async function redirectAuth(userId: string) {
  const config = {
    headers: {
      'Moodle-ID': userId,
    },
    withCredentials: false,
  };
  axios.get(API_URL + '/oauth/bind/', config).then((res) => {
    if (res.status === 200) {
      chrome.tabs.create({ url: res.data });
    } else {
      console.error('Auth failed');
    }
  });
}

async function checkLoginStatus(tabs: chrome.tabs.Tab[], sendResponse: (res?: any) => void) {
  if (tabs.length === 0) {
    // no active tab moodle tab found
    sendResponse({ loggedIn: false });
  } else {
    // check if any of the tabs has the user logged in
    let ret = {
      loggedIn: false,
      userId: null,
    };
    for (const tab of tabs) {
      const response = await chrome.tabs.sendMessage(tab.id!, { action: 'checkLogin' });
      if (response.loggedIn) {
        ret = response;
        break;
      }
    }
    sendResponse(ret);
  }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'checkLogin':
      // check if there is an active moodle tab
      chrome.tabs.query({ url: MOODLE_URL }, (tabs) => {
        checkLoginStatus(tabs, sendResponse);
      });
      break;
    case 'bindAccount':
      redirectAuth(request.userId);
      break;
    case 'getMoodleSession':
      getMoodleSession().then((res) => {
        sendResponse({ moodleSession: res });
      });
      break;
  }
  return true;
});

export {};
