import './BindAccount.css';

interface Props {
  isMain: boolean;
  switchAcc: boolean;
  onBind: () => void;
}

export default function BindAccount({ isMain = false, switchAcc, onBind }: Props) {
  const textClass = isMain ? 'main-text enabled-text' : 'secondary-text';
  return (
    <button className={isMain ? 'main-btn' : 'secondary-btn'} onClick={onBind}>
      <img
        className='icon'
        src={process.env.PUBLIC_URL + '/images/google_icon.png'}
        alt='google icon'
      />
      <span className={textClass}>{switchAcc ? '切換帳號' : '綁定帳號'}</span>
    </button>
  );
}
