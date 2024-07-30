function getUserId(): string | null {
  const element = document.querySelector('.popover-region.collapsed.popover-region-notifications');
  if (element === null) {
    return null;
  }
  return element?.getAttribute('data-userid');
}

function isLoggedIn() {
  if (
    document.getElementsByClassName('login').length === 0 &&
    window.location.href !== 'https://moodle.ncku.edu.tw/login/index.php'
  ) {
    return true;
  } else {
    return false;
  }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'checkLogin':
      if (isLoggedIn()) {
        sendResponse({ loggedIn: true, userId: getUserId() });
      } else {
        sendResponse({ loggedIn: false });
      }
      break;
  }
});

export {};
