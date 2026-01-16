# Textarea Text Color & Image Index Fix

## Issues Fixed

### 1. ✅ Textarea Text is Gray (Hard to Read)
**Problem:** Text typed in the textarea was gray, making it difficult to read on white background

**Solution:** Added `text-gray-900` class to textarea:
```tsx
<textarea
  className="w-full px-4 py-3 border border-gray-300 rounded-lg 
             focus:ring-2 focus:ring-purple-600 focus:border-transparent 
             resize-none text-gray-900"
  // ... other props
/>
```

**Result:** Text is now black/dark gray and clearly readable

**File:** `viral-story-search/src/components/CharacterImageDisplay.tsx`

---

### 2. ✅ Second Image Shows as 3 Instead of 2
**Problem:** When generating the second image, it would show "3/2" instead of "2/2"

**Root Cause:** The previous `useEffect` was running on EVERY `images.length` change, including:
- Initial render
- Character switches
- Component re-renders

This caused the index to jump incorrectly.

**Solution:** Use `useRef` to track the previous length and only update when length INCREASES:

```tsx
const prevImagesLengthRef = useRef(images.length);

// Reset when character changes
useEffect(() => {
  setDescription(character.visual_description);
  setCurrentImageIndex(0);
  prevImagesLengthRef.current = images.length;
}, [character.name]);

// Only update when NEW image is added
useEffect(() => {
  if (images.length > prevImagesLengthRef.current) {
    // New image was added, show it
    setCurrentImageIndex(images.length - 1);
  }
  prevImagesLengthRef.current = images.length;
}, [images.length]);
```

**How It Works:**
1. `prevImagesLengthRef` stores the previous images array length
2. When `images.length` changes, we check if it INCREASED
3. Only if it increased (new image added), we update the index to show the latest
4. We update the ref to track the new length

**Result:** 
- First image: Shows 1/1 ✅
- Second image: Shows 2/2 ✅ (not 3/2)
- Third image: Shows 3/3 ✅ (not 5/3)

**File:** `viral-story-search/src/components/CharacterImageDisplay.tsx`

---

## Testing

### Test Textarea Readability
1. Select a character
2. Type in the description textarea
3. Text should be clearly visible (black/dark gray)

### Test Image Index
1. Generate first image for Character A
   - Should show: "1 / 1" ✅
2. Generate second image for Character A
   - Should show: "2 / 2" ✅ (not 3/2)
3. Generate third image for Character A
   - Should show: "3 / 3" ✅ (not 5/3)
4. Switch to Character B
   - Should reset to show first image: "1 / 1" ✅
5. Generate image for Character B
   - Should show: "2 / 2" ✅

---

## Technical Details

### Why useRef Instead of useState?

`useRef` is perfect for tracking previous values because:
- ✅ Doesn't trigger re-renders when updated
- ✅ Persists across renders
- ✅ Mutable without causing side effects
- ✅ Perfect for comparison logic

### Why Two useEffect Hooks?

1. **First useEffect** (character.name dependency):
   - Resets state when switching characters
   - Ensures clean slate for each character
   - Updates ref to current length

2. **Second useEffect** (images.length dependency):
   - Only runs when images array changes
   - Compares with previous length
   - Only updates index if length INCREASED
   - Updates ref for next comparison

This separation of concerns makes the logic clear and prevents bugs.

---

## Files Modified

1. `viral-story-search/src/components/CharacterImageDisplay.tsx`
   - Added `text-gray-900` to textarea className
   - Added `useRef` to track previous images length
   - Split logic into two useEffect hooks
   - Fixed image index calculation

---

## Before vs After

### Textarea Text Color
| Before | After |
|--------|-------|
| Gray text (hard to read) | Black text (clearly visible) |
| No text-color class | `text-gray-900` class |

### Image Index Behavior
| Action | Before | After |
|--------|--------|-------|
| Generate 1st image | 1/1 ✅ | 1/1 ✅ |
| Generate 2nd image | 3/2 ❌ | 2/2 ✅ |
| Generate 3rd image | 5/3 ❌ | 3/3 ✅ |
| Switch character | Wrong index ❌ | Resets to 0 ✅ |
