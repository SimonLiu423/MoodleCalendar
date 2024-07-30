import { useEffect, useState } from 'react';
import './App.css';
import AccountStatus from './components/AccountStatus';
import BindAccount from './components/BindAccount';
import Sync from './components/Sync';
import { API_URL } from './constants';
import axios from 'axios';

interface AppState {
  checkingStatus: boolean;
  loggedIn: boolean;
  email: string | null;
  errorMsg: string;
  loading: boolean;
  success: boolean;
  userId: string | null;
}

function App() {
  const [state, setState] = useState<AppState>({
    checkingStatus: true,
    loggedIn: false,
    email: null,
    userId: null,
    errorMsg: '',
    loading: false,
    success: false,
  });

  async function getBoundEmail(userId: string | null): Promise<string | null> {
    const config = {
      headers: {
        'Moodle-ID': userId,
      },
      withCredentials: false,
    };
    try {
      const res = await axios.get(API_URL + '/oauth/status/', config);
      return res.data;
    } catch (err) {
      setState((state) => ({ ...state, errorMsg: '無法連線至伺服器' }));
      console.log(err);
    }
    return null;
  }

  function resetState() {
    setState((state) => ({
      ...state,
      errorMsg: '',
      success: false,
      loading: false,
    }));
  }

  function handleBind() {
    resetState();
    chrome.runtime.sendMessage({ action: 'bindAccount', userId: state.userId });
  }

  function handleSync() {
    resetState();
    setState((state) => ({ ...state, loading: true }));
    chrome.runtime.sendMessage({ action: 'getMoodleSession' }).then((res) => {
      const config = {
        headers: {
          'Moodle-ID': state.userId,
          'Moodle-Session': res.moodleSession,
        },
      };
      axios
        .post(API_URL + '/calendar_sync/sync/', {}, config)
        .then((res) => {
          setState((state) => ({ ...state, loading: false }));
          if (res.status === 200) {
            setState((state) => ({ ...state, success: true }));
          } else {
            setState((state) => ({ ...state, success: false, errorMsg: '同步失敗' }));
          }
        })
        .catch((err) => {
          setState((state) => ({ ...state, loading: false, errorMsg: '同步失敗' }));
          console.log(err);
        });
    });
  }

  useEffect(() => {
    chrome.runtime.sendMessage({ action: 'checkLogin' }).then((res) => {
      (async () => {
        let email: string | null = null;
        if (res.loggedIn) {
          email = await getBoundEmail(res.userId);
        }
        setState((state) => ({
          ...state,
          checkingStatus: false,
          loggedIn: res.loggedIn,
          email: email,
          userId: res.userId,
        }));
      })();
    });
  }, []);

  if (state.checkingStatus) {
    return (
      <div className='App'>
        <img className='logo' src={process.env.PUBLIC_URL + '/images/logo.png'} alt='logo' />
        <div className='loader' />
      </div>
    );
  }

  if (state.loggedIn === false) {
    return (
      <div className='App'>
        <img className='logo' src={process.env.PUBLIC_URL + '/images/logo.png'} alt='logo' />
        <Sync
          enabled={false}
          isSuccess={false}
          errorMsg={'請先登入Moodle'}
          loading={state.loading}
          onSync={handleSync}
        />
      </div>
    );
  }

  if (state.email == null) {
    if (state.errorMsg === '') {
      return (
        <div className='App'>
          <img className='logo' src={process.env.PUBLIC_URL + '/images/logo.png'} alt='logo' />
          <BindAccount isMain={true} switchAcc={false} onBind={handleBind} />
        </div>
      );
    } else {
      return (
        <div className='App'>
          <img className='logo' src={process.env.PUBLIC_URL + '/images/logo.png'} alt='logo' />
          <div className='error-text' style={{ color: 'white', fontSize: '14px' }}>
            {state.errorMsg}
          </div>
        </div>
      );
    }
  }

  return (
    <div className='App'>
      <img className='logo' src={process.env.PUBLIC_URL + '/images/logo.png'} alt='logo' />
      <Sync
        enabled={true}
        isSuccess={state.success}
        errorMsg={state.errorMsg}
        onSync={handleSync}
        loading={state.loading}
      />
      <BindAccount isMain={false} switchAcc={true} onBind={handleBind} />
      <AccountStatus email={state.email} />
    </div>
  );
}

export default App;
