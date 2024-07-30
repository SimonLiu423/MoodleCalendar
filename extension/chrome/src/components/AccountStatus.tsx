import './AccountStatus.css';

export default function AccountStatus({ email }: { email: string }) {
  return (
    <div className='account-status'>
      <span>{'  目前帳號：'}</span>
      <span>{email}</span>
    </div>
  );
}
