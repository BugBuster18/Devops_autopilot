import { SessionProvider } from 'next-auth/react';
import '../styles/globals.css'; // Assuming you have global styles
import '../styles/mcu-animations.css'; // MCU-themed animations

export default function App({ Component, pageProps: { session, ...pageProps } }) {
  return (
    <SessionProvider session={session}>
      <Component {...pageProps} />
    </SessionProvider>
  );
}
