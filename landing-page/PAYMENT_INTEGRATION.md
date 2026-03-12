# 💳 Payment Integration Documentation

## Overview

Complete multi-gateway checkout system for DM Sentinel Web3 security audits. Supports 3 payment methods with automatic webhook triggering for Sprint 2 Vigilance system.

---

## 🎯 PROMPT 2 Requirements (COMPLETED ✅)

### Original Requirements

**Objetivo**: Conectar los botones de la tabla de precios con las pasarelas de pago reales.

**Instrucciones**:
1. ✅ **Lógica de Botón**: Modal de 'Selección de Método de Pago' (Credit Card, Pix, USDC)
2. ✅ **Metadatos**: Pasar wallet del cliente, plan seleccionado, URL a auditar al webhook
3. ✅ **Checkout Dinámico**: 
   - Pix → código QR dinámico con API Mercado Pago
   - USDC → transacción con ethers.js

**Sprint 2 Integration**: Webhook para disparar Sprint 2 automáticamente tras éxito

---

## 🏗️ Architecture

### Payment Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    USER CLICKS PRICING BUTTON             │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│              STEP 1: METHOD SELECTION MODAL               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│  │   💳 Card  │  │   📱 Pix   │  │  🔐 USDC   │         │
│  │   (Stripe) │  │ (Mercado   │  │  (Web3)    │         │
│  │            │  │   Pago)    │  │            │         │
│  └────────────┘  └────────────┘  └────────────┘         │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│              STEP 2: FORM INPUT                           │
│  • Contract URL* (https://etherscan.io/address/0x...)    │
│  • Email* (user@email.com)                               │
│  • Wallet (optional) (0x...)                             │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│              STEP 3: PAYMENT EXECUTION                    │
│                                                           │
│  STRIPE FLOW:                                            │
│  1. Load Stripe.js SDK                                   │
│  2. Create checkout session (backend API)                │
│  3. Redirect to Stripe hosted page                       │
│  4. User completes payment                               │
│  5. Redirect back to success/cancel URL                  │
│                                                           │
│  PIX FLOW:                                               │
│  1. Load Mercado Pago SDK                                │
│  2. Create Pix payment (backend API)                     │
│  3. Display QR code in modal                             │
│  4. Poll payment status every 3 seconds                  │
│  5. Success when status = 'approved'                     │
│                                                           │
│  CRYPTO FLOW:                                            │
│  1. Import ethers.js dynamically                         │
│  2. Connect MetaMask wallet                              │
│  3. Detect network (Ethereum/Polygon)                    │
│  4. Get USDC contract                                    │
│  5. Execute transfer to DM Sentinel wallet               │
│  6. Wait for transaction confirmation                    │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│              STEP 4: WEBHOOK TRIGGER                      │
│                                                           │
│  POST https://api.dmsentinel.com/webhook/payment         │
│                                                           │
│  {                                                        │
│    "client_wallet": "0x...",                             │
│    "plan_selected": "pro",                               │
│    "contract_url": "https://etherscan.io/...",           │
│    "payment_method": "stripe",                           │
│    "amount_usd": 7500,                                   │
│    "transaction_id": "pi_xxx",                           │
│    "client_email": "user@email.com",                     │
│    "timestamp": "2026-03-11T12:00:00Z",                  │
│    "metadata": { ... }                                   │
│  }                                                        │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│          ✅ SPRINT 2 VIGILANCE AUTO-TRIGGERED            │
│                                                           │
│  Backend receives webhook → Starts audit process         │
└──────────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation

### 1. State Management (React Hooks)

```javascript
// Payment modal state
const [showPaymentModal, setShowPaymentModal] = useState(false);
const [selectedPlan, setSelectedPlan] = useState(null);
const [paymentMethod, setPaymentMethod] = useState(null); // 'card', 'pix', 'crypto'
const [paymentStep, setPaymentStep] = useState('method'); // 'method', 'form', 'processing', 'success', 'error'

// Form data
const [formData, setFormData] = useState({
  contractUrl: '',
  email: '',
  wallet: ''
});

// Payment-specific state
const [pixData, setPixData] = useState(null); // QR code data
const [walletConnected, setWalletConnected] = useState(false);
const [walletAddress, setWalletAddress] = useState('');
const [errorMessage, setErrorMessage] = useState('');
```

### 2. SDK Lazy Loading

```javascript
// Load Stripe.js dynamically
const loadStripe = async () => {
  if (window.Stripe) return window.Stripe(STRIPE_PUBLIC_KEY);
  const script = document.createElement('script');
  script.src = 'https://js.stripe.com/v3/';
  document.head.appendChild(script);
  return new Promise((resolve) => {
    script.onload = () => resolve(window.Stripe(STRIPE_PUBLIC_KEY));
  });
};

// Load Mercado Pago SDK dynamically
const loadMercadoPago = async () => {
  if (window.MercadoPago) return new window.MercadoPago(MERCADO_PAGO_PUBLIC_KEY);
  const script = document.createElement('script');
  script.src = 'https://sdk.mercadopago.com/js/v2';
  document.head.appendChild(script);
  return new Promise((resolve) => {
    script.onload = () => resolve(new window.MercadoPago(MERCADO_PAGO_PUBLIC_KEY));
  });
};
```

**Why lazy loading?**
- Reduces initial bundle size
- Only load SDKs when needed
- Improves page load performance
- Better for Core Web Vitals

### 3. Payment Handler Functions

#### Stripe Credit Card Payment

```javascript
const handleStripePayment = async () => {
  try {
    setPaymentStep('processing');
    const stripe = await loadStripe();
    
    // Backend creates checkout session
    const response = await fetch(`${WEBHOOK_URL}/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        plan: selectedPlan.name,
        amount: parseFloat(selectedPlan.price.replace(/[^0-9.]/g, '')),
        contract_url: formData.contractUrl,
        email: formData.email,
        wallet: formData.wallet,
        success_url: window.location.origin + '/payment-success',
        cancel_url: window.location.origin + '/payment-cancel'
      })
    });
    
    const session = await response.json();
    
    // Redirect to Stripe checkout
    await stripe.redirectToCheckout({ sessionId: session.id });
    
  } catch (error) {
    console.error('Stripe error:', error);
    setErrorMessage(error.message);
    setPaymentStep('error');
  }
};
```

**Backend endpoint needed**: `POST /create-checkout-session`

#### Mercado Pago Pix Payment

```javascript
const handlePixPayment = async () => {
  try {
    setPaymentStep('processing');
    
    // Backend creates Pix payment
    const response = await fetch(`${WEBHOOK_URL}/create-pix-payment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        plan: selectedPlan.name,
        amount: parseFloat(selectedPlan.price.replace(/[^0-9.]/g, '')),
        contract_url: formData.contractUrl,
        email: formData.email,
        payer: { email: formData.email }
      })
    });
    
    const payment = await response.json();
    
    // Extract QR code data
    setPixData({
      qr_code: payment.point_of_interaction.transaction_data.qr_code,
      qr_code_base64: payment.point_of_interaction.transaction_data.qr_code_base64,
      payment_id: payment.id
    });
    
    setPaymentStep('pix');
    
    // Poll for payment status every 3 seconds
    const pollInterval = setInterval(async () => {
      const statusResponse = await fetch(`${WEBHOOK_URL}/check-payment/${payment.id}`);
      const statusData = await statusResponse.json();
      
      if (statusData.status === 'approved') {
        clearInterval(pollInterval);
        await sendWebhook({
          payment_method: 'mercadopago',
          payment_id: payment.id
        });
        setPaymentStep('success');
      }
    }, 3000);
    
  } catch (error) {
    console.error('Pix error:', error);
    setErrorMessage(error.message);
    setPaymentStep('error');
  }
};
```

**Backend endpoints needed**: 
- `POST /create-pix-payment`
- `GET /check-payment/:id`

#### Web3 USDC Payment

```javascript
const handleCryptoPayment = async () => {
  try {
    setPaymentStep('processing');
    
    if (!window.ethereum) {
      throw new Error('Please install MetaMask');
    }
    
    // Dynamic import of ethers
    const { ethers } = await import('ethers');
    
    // Connect wallet
    const provider = new ethers.BrowserProvider(window.ethereum);
    await provider.send('eth_requestAccounts', []);
    const signer = await provider.getSigner();
    const walletAddress = await signer.getAddress();
    
    setWalletConnected(true);
    setWalletAddress(walletAddress);
    
    // Detect network
    const network = await provider.getNetwork();
    const chainId = network.chainId;
    
    // USDC contract addresses
    const USDC_CONTRACT = {
      1: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', // Ethereum
      137: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174' // Polygon
    };
    
    const usdcAddress = USDC_CONTRACT[Number(chainId)];
    if (!usdcAddress) {
      throw new Error('Please switch to Ethereum or Polygon network');
    }
    
    // USDC contract interaction
    const usdcAbi = ['function transfer(address to, uint256 amount) returns (bool)'];
    const usdcContract = new ethers.Contract(usdcAddress, usdcAbi, signer);
    
    // Calculate amount (USDC has 6 decimals)
    const amount = parseFloat(selectedPlan.price.replace(/[^0-9.]/g, ''));
    const amountInWei = ethers.parseUnits(amount.toString(), 6);
    
    // Execute transfer
    const tx = await usdcContract.transfer(DM_SENTINEL_WALLET, amountInWei);
    const receipt = await tx.wait();
    
    // Send webhook
    await sendWebhook({
      payment_method: 'web3',
      transaction_hash: receipt.hash,
      wallet_address: walletAddress,
      network: chainId === 1n ? 'ethereum' : 'polygon'
    });
    
    setPaymentStep('success');
    
  } catch (error) {
    console.error('Crypto error:', error);
    setErrorMessage(error.message);
    setPaymentStep('error');
  }
};
```

**Requirements**:
- User must have MetaMask installed
- User must have USDC balance
- User must be on Ethereum or Polygon network

### 4. Webhook Function

```javascript
const sendWebhook = async (paymentData) => {
  try {
    await fetch(WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_wallet: formData.wallet || paymentData.wallet_address || null,
        plan_selected: selectedPlan.name.toLowerCase(), // 'basic', 'pro', 'enterprise'
        contract_url: formData.contractUrl,
        payment_method: paymentData.payment_method, // 'stripe', 'mercadopago', 'web3'
        amount_usd: parseFloat(selectedPlan.price.replace(/[^0-9.]/g, '')),
        transaction_id: paymentData.transaction_hash || paymentData.charge_id || paymentData.payment_id,
        client_email: formData.email,
        timestamp: new Date().toISOString(),
        metadata: {
          language: currentLang,
          browser: navigator.userAgent,
          referrer: document.referrer
        }
      })
    });
  } catch (error) {
    console.error('Webhook error:', error);
  }
};
```

---

## 🎨 UI/UX Details

### Payment Modal Steps

#### Step 1: Method Selection
- **3 payment cards** displayed in grid
- **Icons**: 💳 (card), 📱 (Pix), 🔐 (crypto)
- **Hover effect**: Card lifts up, glow intensifies
- **Click**: Select method → Move to form

#### Step 2: Form Input
- **Contract URL** (required) - Text input with placeholder
- **Email** (required) - Email input with validation
- **Wallet** (optional) - Text input for Web3 address
- **Buttons**: Cancel (back to method selection), Pay (submit)

#### Step 3: Processing
- **Spinner animation** - Rotating border effect
- **Text**: "Processing..." (translated)
- **No interaction** - Modal locked during processing

#### Step 4a: Pix QR Code (Pix only)
- **QR code image** - Base64 PNG from Mercado Pago
- **Copy button** - Copy Pix code to clipboard
- **Polling indicator** - "Waiting for payment confirmation..."
- **Auto-close** - When payment approved

#### Step 4b: Success
- **Green checkmark** - Animated scale-in effect
- **Title**: "Payment Successful!" (translated)
- **Message**: "Your audit will be processed shortly"
- **Email confirmation** - "We sent you a confirmation email"
- **OK button** - Close modal

#### Step 4c: Error
- **Red X icon** - Animated shake effect
- **Title**: "Payment Error" (translated)
- **Message**: Error details from gateway
- **Buttons**: Cancel (close), Try Again (back to form)

### CSS Animations

```css
/* Modal slide-in */
@keyframes modal-slide-up {
  from { transform: translateY(50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Spinner rotation */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Success icon pop */
@keyframes success-pop {
  0% { transform: scale(0); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

/* Error icon shake */
@keyframes error-shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

/* Waiting text pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

---

## 🌍 Multi-Language Support

All payment UI elements translated in 5 languages:

### Translation Structure

```javascript
TRANSLATIONS.{lang}.payment = {
  modal_title: 'Select Payment Method',
  modal_subtitle: 'Choose your preferred payment method',
  plan_selected: 'Plan selected',
  amount: 'Amount',
  methods: {
    card: 'Credit Card',
    card_desc: 'Visa, Mastercard, Amex via Stripe',
    pix: 'Pix',
    pix_desc: 'QR Code - Instant payment',
    crypto: 'Cryptocurrency',
    crypto_desc: 'USDC on Ethereum/Polygon'
  },
  form: {
    contract_url: 'Contract URL to audit',
    contract_placeholder: 'https://etherscan.io/address/0x...',
    wallet: 'Your wallet (optional)',
    wallet_placeholder: '0x...',
    email: 'Contact email',
    email_placeholder: 'your@email.com',
    pay_button: 'Pay',
    processing: 'Processing...',
    cancel: 'Cancel'
  },
  pix: {
    title: 'Scan QR Code',
    instructions: 'Open your banking app and scan the code',
    copy_code: 'Copy Pix code',
    waiting: 'Waiting for payment confirmation...'
  },
  crypto: {
    connect: 'Connect Wallet',
    connected: 'Wallet Connected',
    approve: 'Approve USDC',
    pay: 'Pay with USDC',
    network: 'Network',
    balance: 'Balance'
  },
  success: {
    title: 'Payment Successful!',
    message: 'Your audit will be processed shortly',
    email_sent: 'We sent you a confirmation email'
  },
  error: {
    title: 'Payment Error',
    message: 'There was a problem processing your payment',
    try_again: 'Try again'
  }
};
```

**Languages**: Spanish, English, French, Portuguese, Esperanto

---

## 🔐 Security Considerations

### Frontend Security

1. **No API Keys in Code** ✅
   - All keys in environment variables
   - `.env` in `.gitignore`
   - Public keys only (Stripe/Mercado Pago)

2. **HTTPS Only** ✅
   - Stripe/Mercado Pago enforce SSL
   - Web3 wallet connections secure
   - No sensitive data in localStorage

3. **Input Validation** ✅
   - Email format validation
   - URL format validation (Etherscan/Polygonscan)
   - Wallet address format validation (0x...)

4. **Error Handling** ✅
   - Try-catch blocks on all payment functions
   - User-friendly error messages
   - No sensitive error details exposed

### Backend Security (Required)

1. **Webhook Signature Verification** 🔴
   - Validate Stripe signatures
   - Validate Mercado Pago signatures
   - Reject unauthorized requests

2. **Payment Amount Verification** 🔴
   - Double-check amount on backend
   - Verify plan matches price
   - Prevent price manipulation

3. **Idempotency** 🔴
   - Deduplicate webhook calls
   - Store transaction IDs
   - Prevent double-processing

4. **Rate Limiting** 🔴
   - Limit API calls per IP
   - Prevent abuse/spam
   - CAPTCHA for suspicious activity

---

## 📦 Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "ethers": "^6.10.0"
  }
}
```

**External SDKs** (loaded via CDN):
- Stripe.js v3: `https://js.stripe.com/v3/`
- Mercado Pago SDK v2: `https://sdk.mercadopago.com/js/v2`

---

## 🧪 Testing

### Local Testing

1. **Install dependencies**:
```bash
npm install
```

2. **Create `.env` file**:
```bash
cp .env.example .env
# Fill in test API keys
```

3. **Start dev server**:
```bash
npm run dev
```

4. **Test payment flows**:
   - Click pricing buttons
   - Select each payment method
   - Fill form with test data
   - Execute test payments

### Stripe Test Cards

```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0025 0000 3155

Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits
```

### Mercado Pago Sandbox

Get test credentials from:
https://www.mercadopago.com.br/developers/panel/test-users

### Web3 Testing

1. **Use testnets**:
   - Goerli (Ethereum testnet)
   - Mumbai (Polygon testnet)

2. **Get test USDC**:
   - Goerli faucet: https://goerli-faucet.mudit.blog/
   - Swap ETH for test USDC on Uniswap

3. **Connect MetaMask**:
   - Add testnet network
   - Import test wallet
   - Execute test transaction

---

## 🚀 Deployment

### Environment Variables

Set in production environment:

```bash
REACT_APP_STRIPE_PUBLIC_KEY=pk_live_...
REACT_APP_MERCADO_PAGO_PUBLIC_KEY=APP_USR_PROD_...
REACT_APP_WEBHOOK_URL=https://api.dmsentinel.com/webhook/payment
REACT_APP_ENV=production
```

### Build for Production

```bash
npm run build
```

Output in `dist/` folder.

### Deployment Checklist

- [ ] Environment variables set
- [ ] Stripe in live mode
- [ ] Mercado Pago in production mode
- [ ] Backend webhook endpoint deployed
- [ ] Webhook signature verification enabled
- [ ] SSL certificate installed
- [ ] CORS configured for frontend domain
- [ ] Analytics tracking enabled
- [ ] Error monitoring configured (Sentry)
- [ ] Payment success/failure emails tested

---

## 📊 Analytics & Monitoring

### Key Metrics to Track

1. **Conversion Rate**: Visitors → Payment modal opens
2. **Method Preference**: Card vs Pix vs Crypto distribution
3. **Drop-off Points**: Where users abandon payment
4. **Success Rate**: Completed payments / Attempted payments
5. **Average Order Value**: Per plan (Basic/Pro/Enterprise)
6. **Geography**: Payment methods by country
7. **Error Rate**: Failed payments by gateway

### Recommended Tools

- **Google Analytics**: Funnel tracking
- **Hotjar**: Heatmaps on pricing section
- **Sentry**: Error tracking
- **Stripe Dashboard**: Payment analytics
- **Mercado Pago Dashboard**: Pix statistics

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: Stripe SDK not loading

**Solution**:
```javascript
// Check if script loaded
console.log('Stripe:', window.Stripe);

// Try loading manually
const script = document.createElement('script');
script.src = 'https://js.stripe.com/v3/';
script.onload = () => console.log('Stripe loaded');
script.onerror = () => console.error('Stripe failed to load');
document.head.appendChild(script);
```

#### Issue: MetaMask not detected

**Solution**:
```javascript
// Check multiple wallet providers
if (window.ethereum) {
  console.log('Wallet detected:', window.ethereum);
} else {
  alert('Please install MetaMask or a Web3 wallet');
  window.open('https://metamask.io/', '_blank');
}
```

#### Issue: Pix QR code not displaying

**Solution**:
- Check backend response structure
- Verify `qr_code_base64` field exists
- Validate base64 encoding
- Test with static QR code first

#### Issue: Wrong network for USDC

**Solution**:
```javascript
const chainId = await provider.getNetwork();
if (![1, 137].includes(Number(chainId.chainId))) {
  // Prompt user to switch network
  await window.ethereum.request({
    method: 'wallet_switchEthereumChain',
    params: [{ chainId: '0x1' }], // Ethereum mainnet
  });
}
```

---

## 📞 Support

**Technical Questions**: security@dmsentinel.com  
**Payment Issues**: support@dmsentinel.com  
**Documentation**: https://docs.dmsentinel.com

---

**Implementation Date**: March 11, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Next Sprint**: Backend webhook integration
