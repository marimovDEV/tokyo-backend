# 🔧 Next.js Metadata Viewport Warning Fix

## ❌ Muammo

Next.js yangi versiyasida `viewport` va `themeColor` metadata konfiguratsiyasi `metadata` export dan `viewport` export ga ko'chirilishi kerak.

**Sizning xatolaringiz:**
```
⚠ Unsupported metadata viewport is configured in metadata export in /menu
⚠ Unsupported metadata themeColor is configured in metadata export in /menu
⚠ Unsupported metadata viewport is configured in metadata export in /
⚠ Unsupported metadata themeColor is configured in metadata export in /
⚠ Unsupported metadata viewport is configured in metadata export in /waiter
⚠ Unsupported metadata themeColor is configured in metadata export in /waiter
```

---

## ✅ Yechim

### Ta'sirlangan fayllar:
1. `app/page.tsx` - root page
2. `app/menu/page.tsx` - menu page
3. `app/waiter/page.tsx` - waiter page

---

## 📝 Qanday Tuzatish Kerak

### ❌ **ESKI USUL (ishlamaydi):**

```typescript
// app/page.tsx
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Tokyo Kafe',
  description: 'Tokyo Kafe Restaurant',
  viewport: 'width=device-width, initial-scale=1',  // ❌ Eskirgan
  themeColor: '#9333ea',  // ❌ Eskirgan
}

export default function Page() {
  return <div>...</div>
}
```

### ✅ **YANGI USUL (to'g'ri):**

```typescript
// app/page.tsx
import { Metadata, Viewport } from 'next'

// Metadata (viewport va themeColor siz)
export const metadata: Metadata = {
  title: 'Tokyo Kafe',
  description: 'Tokyo Kafe Restaurant',
  // viewport va themeColor ni bu yerda yozmaslik!
}

// Viewport alohida eksport
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#9333ea',
}

export default function Page() {
  return <div>...</div>
}
```

---

## 🛠️ Har Bir Fayl Uchun Tuzatish

### 1️⃣ `app/page.tsx` - Root Page

**Eski kod:**
```typescript
export const metadata: Metadata = {
  title: 'Tokyo Kafe',
  description: 'Tokyo Kafe - Eng mazali taomlar',
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#9333ea',
}
```

**Yangi kod:**
```typescript
import { Metadata, Viewport } from 'next'

export const metadata: Metadata = {
  title: 'Tokyo Kafe',
  description: 'Tokyo Kafe - Eng mazali taomlar',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#9333ea',
}
```

---

### 2️⃣ `app/menu/page.tsx` - Menu Page

**Eski kod:**
```typescript
export const metadata: Metadata = {
  title: 'Menyu | Tokyo Kafe',
  description: 'Tokyo Kafe menyusi',
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#9333ea',
}
```

**Yangi kod:**
```typescript
import { Metadata, Viewport } from 'next'

export const metadata: Metadata = {
  title: 'Menyu | Tokyo Kafe',
  description: 'Tokyo Kafe menyusi',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#9333ea',
}
```

---

### 3️⃣ `app/waiter/page.tsx` - Waiter Page

**Eski kod:**
```typescript
export const metadata: Metadata = {
  title: 'Ofitsiant | Tokyo Kafe',
  description: 'Tokyo Kafe ofitsiant paneli',
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#9333ea',
}
```

**Yangi kod:**
```typescript
import { Metadata, Viewport } from 'next'

export const metadata: Metadata = {
  title: 'Ofitsiant | Tokyo Kafe',
  description: 'Tokyo Kafe ofitsiant paneli',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#9333ea',
}
```

---

## 🎯 Viewport Konfiguratsiya Opsiyalari

`Viewport` type quyidagi opsiyalarni qo'llab-quvvatlaydi:

```typescript
export const viewport: Viewport = {
  width: 'device-width',           // Viewport kengligi
  initialScale: 1,                 // Boshlang'ich zoom
  maximumScale: 1,                 // Maksimal zoom
  minimumScale: 1,                 // Minimal zoom
  userScalable: false,             // Foydalanuvchi zoom qila oladimi
  themeColor: '#9333ea',           // Browser theme rangi
  colorScheme: 'dark',             // 'light' | 'dark' | 'light dark'
  
  // Yoki dynamic qilish:
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#000000' },
  ],
}
```

---

## 🔄 Agar `layout.tsx` da ham bo'lsa

Agar root `app/layout.tsx` da ham shu muammo bo'lsa:

**Eski:**
```typescript
// app/layout.tsx
export const metadata: Metadata = {
  title: 'Tokyo Kafe',
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#9333ea',
}
```

**Yangi:**
```typescript
// app/layout.tsx
import { Metadata, Viewport } from 'next'

export const metadata: Metadata = {
  title: 'Tokyo Kafe',
  // viewport va themeColor yo'q
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#9333ea',
}
```

---

## 📚 To'liq Misol

```typescript
// app/page.tsx - To'liq misol
import { Metadata, Viewport } from 'next'

export const metadata: Metadata = {
  title: 'Tokyo Kafe',
  description: 'Eng mazali taomlar Tokyo Kafe da',
  keywords: ['restaurant', 'tokyo', 'sushi', 'japanese food'],
  authors: [{ name: 'Tokyo Kafe Team' }],
  openGraph: {
    title: 'Tokyo Kafe',
    description: 'Eng mazali taomlar',
    images: ['/og-image.jpg'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Tokyo Kafe',
    description: 'Eng mazali taomlar',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#000000' },
  ],
  colorScheme: 'light dark',
}

export default function Home() {
  return (
    <main>
      <h1>Tokyo Kafe</h1>
    </main>
  )
}
```

---

## 🚀 Tezkor Tuzatish Qadamlari

### 1. Barcha page.tsx fayllarni toping:
```bash
find . -name "page.tsx" -o -name "layout.tsx"
```

### 2. Har birida quyidagilarni qiling:

**Import qo'shish:**
```typescript
import { Metadata, Viewport } from 'next'
```

**metadata dan viewport/themeColor ni olib tashlash:**
```typescript
export const metadata: Metadata = {
  title: '...',
  description: '...',
  // viewport va themeColor ni o'chirish
}
```

**Yangi viewport export qo'shish:**
```typescript
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#9333ea',
}
```

### 3. Rebuild qilish:
```bash
npm run build
# yoki
yarn build
# yoki
pnpm build
```

---

## ✅ Natija

Endi warning yo'qoladi va sizning build clean bo'ladi:
```
✓ Generating static pages (9/9)
✓ Finalizing page optimization
✓ Collecting build traces
```

---

## 📖 Qo'shimcha Ma'lumot

- **Next.js Docs**: https://nextjs.org/docs/app/api-reference/functions/generate-viewport
- **Migration Guide**: https://nextjs.org/docs/messages/app-metadata-viewport

---

## 🎓 Dynamic Viewport (Advanced)

Agar har bir sahifa uchun turli xil viewport kerak bo'lsa:

```typescript
// app/menu/page.tsx
import { Viewport } from 'next'

export const viewport: Viewport = {
  themeColor: '#ef4444', // Qizil
}

// app/waiter/page.tsx
export const viewport: Viewport = {
  themeColor: '#10b981', // Yashil
}
```

Yoki function bilan dynamic qilish:

```typescript
import { Viewport } from 'next'

export function generateViewport(): Viewport {
  return {
    width: 'device-width',
    initialScale: 1,
    themeColor: process.env.THEME_COLOR || '#9333ea',
  }
}
```

---

**Tokyo Kafe** 🍽️  
Next.js Metadata Migration Guide 2025

