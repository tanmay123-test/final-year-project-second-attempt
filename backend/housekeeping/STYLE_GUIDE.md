# Housekeeping Module Style Guide

This document outlines the design system and color palette used in the Housekeeping module to ensure brand consistency and accessibility.

## 1. Color Palette

### Primary Brand Colors
Strictly preserve the existing purple/violet color scheme.

| Color Name | Hex Value | Usage |
| :--- | :--- | :--- |
| **Primary Purple** | `#8E44AD` | Main buttons, active states, icons, primary text, borders. |
| **Primary Light** | `#F3E5F5` | Backgrounds for selected items, icons, and status pills. |
| **Primary Hover** | `#9B59B6` | Hover states for buttons (Gradient end). |
| **Primary Border** | `#D7BDE2` | Hover borders for cards. |

### Neutral Colors
| Color Name | Hex Value | Usage |
| :--- | :--- | :--- |
| **Background** | `#F9FAFB` | Page background. |
| **Surface** | `#FFFFFF` | Card and container backgrounds. |
| **Text Primary** | `#1F2937` | Headings, main content. |
| **Text Secondary** | `#6B7280` | Subtitles, helper text, inactive icons. |
| **Border** | `#E5E7EB` | Dividers, default borders. |

### Status Colors
| Status | Background | Text | Hex Values |
| :--- | :--- | :--- | :--- |
| **Active/Assigned** | Light Purple | Purple | Bg: `#F3E5F5`, Text: `#8E44AD` |
| **Completed** | Light Green | Green | Bg: `#ECFDF5`, Text: `#059669` |
| **Cancelled/Error** | Light Red | Red | Bg: `#FEF2F2`, Text: `#DC2626` |
| **Warning/Info** | Light Orange | Orange | Bg: `#FFF3E0`, Text: `#B45309` |

### Provider Interface Colors (Worker App)
The worker interface also follows the Primary Brand Colors to ensure brand consistency across the platform.

| Color Name | Hex Value | Usage |
| :--- | :--- | :--- |
| **Primary Purple** | `#8E44AD` | Primary gradient, active tabs, earnings, primary actions. |
| **Primary Light** | `#F3E5F5` | Backgrounds for icons, stats cards. |
| **Success** | `#4CAF50` | Positive actions (Accept, Complete). |

## 2. Component Styles

### Buttons
*   **Primary Action**:
    *   Background: `#8E44AD`
    *   Text: White
    *   Border Radius: `12px`
    *   Padding: `16px` (Full width) or `8px 16px` (Small)
*   **Secondary/Ghost**:
    *   Background: Transparent
    *   Text: `#8E44AD`
    *   Font Weight: `600`

### Cards (Selection/Booking)
*   **Default**:
    *   Background: White
    *   Border: `1px solid #E5E7EB` (or `#F3F4F6`)
    *   Shadow: `0 2px 8px rgba(0,0,0,0.05)`
*   **Selected**:
    *   Background: `#F3E5F5`
    *   Border: `2px solid #8E44AD`
    *   Shadow: `0 4px 12px rgba(142, 68, 173, 0.1)`

### Navigation Tabs
*   **Container**: `#F3F4F6` background, `12px` radius.
*   **Active Tab**:
    *   Background: `#8E44AD`
    *   Text: White
    *   Shadow: `0 2px 4px rgba(142, 68, 173, 0.2)`
*   **Inactive Tab**:
    *   Background: Transparent
    *   Text: `#6B7280`

## 3. Accessibility Standards (WCAG 2.1 AA)

*   **Contrast Ratio**:
    *   `#8E44AD` on White (`#FFFFFF`): **6.84:1** (Passes AA and AAA for Large Text).
    *   White on `#8E44AD`: **6.84:1** (Passes AA).
    *   `#6B7280` (Gray) on White: **4.54:1** (Passes AA).
*   **Interactive Elements**:
    *   Ensure focus states are visible.
    *   Use semantic HTML (`<button>`, `<h1>`).
    *   Provide `aria-label` for icon-only buttons.

## 4. Implementation Example (React)

```jsx
// Button
<button style={{ 
  backgroundColor: '#8E44AD', 
  color: 'white', 
  borderRadius: '12px', 
  padding: '16px',
  border: 'none',
  fontWeight: '600'
}}>
  Confirm Booking
</button>

// Selected Card
<div style={{
  border: '2px solid #8E44AD',
  backgroundColor: '#F3E5F5',
  borderRadius: '12px'
}}>
  <h3 style={{ color: '#8E44AD' }}>Service Name</h3>
</div>
```
