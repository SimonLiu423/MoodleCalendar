import './Sync.css';

interface Props {
  errorMsg: string;
  enabled: boolean;
  isSuccess: boolean;
  loading: boolean;
  onSync: () => void;
}

export default function Sync({ enabled, isSuccess, errorMsg, loading, onSync }: Props) {
  const hasError = errorMsg != '';
  const className = 'main-btn' + (!enabled ? ' disabled' : '') + (hasError ? ' error-btn' : '');
  const textClass = 'main-text' + (enabled ? ' enabled-text' : ' disabled-text');
  return (
    <button className={className} onClick={onSync}>
      <span className={textClass}>同步</span>
      {isSuccess && (
        <img
          className='check-icon'
          src={process.env.PUBLIC_URL + '/images/check.png'}
          alt='check icon'
        />
      )}
      {loading && <div className='sync-loader' />}
      {hasError && <span className='error-text'>{errorMsg}</span>}
    </button>
  );
}
