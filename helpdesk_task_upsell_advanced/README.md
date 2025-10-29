# Helpdesk Task Upsell Advanced

## 🎯 Overview

This module extends **helpdesk_task_upsell** to provide advanced parent/child task hierarchy functionality for managing bulk service operations efficiently.

### The Problem It Solves

When selling services in bulk (e.g., 50 GPS installations), you typically want:
- **One parent service line** in the subscription order (e.g., "GPS Installations - 50 hours")
- **Individual operations** tracked separately (e.g., "Installation: Vehicle ABC-123")
- **Hours to accumulate** in the parent line for proper invoicing
- **Traceability** of each operation without creating separate invoices

Without this module, each operation would create an independent task and invoice line, making it difficult to manage bulk services.

---

## ✨ Key Features

### 1. Parent/Child Task Hierarchy
- Creates **subtasks** under a parent task instead of independent tasks
- Subtasks log hours that accumulate in the parent task
- Maintains clean project structure

### 2. Dual Product System
- **Informative Product**: Used for dummy lines showing operation details (vehicle plates, etc.)
- **Parent Product**: Used for hour accumulation and invoicing

### 3. Automatic Parent Detection
- Finds existing parent tasks in subscription orders
- Creates parent tasks automatically if not found
- Seamlessly integrates with existing workflows

### 4. Smart Line Creation
- Informative lines with zero quantity (no invoicing)
- Hours accumulate in parent product line
- Perfect for subscription-based services

---

## 📋 Use Case Example

### Scenario: GPS Installation Service

**Products Setup:**
1. **"GPS Installations"** (Parent Product)
   - Type: Service
   - Service Tracking: Task in Global Project
   - Service Policy: Based on Timesheets

2. **"Installation"** (Informative Product - auto-created by category)
   - Type: Service
   - Used only for informative lines

**Upsell Category Setup:**
- **Name**: Installation
- **Product**: Installation (informative)
- **Use Parent Task Hierarchy**: ✅ Yes
- **Parent Product**: GPS Installations

**Workflow:**

1. **Sales**: Create subscription order with "GPS Installations - 50 hours"
2. **Operations**: Receive helpdesk ticket for specific installation
3. **FSM Wizard**: 
   - Select "For Upsell" ✅
   - Choose category: "Installation"
   - Select subscription order
   - Enter description: "Vehicle ABC-123"
   - Quantity: 1 hour

**Result in Subscription Order:**
```
GPS Installations                    50h    $5,000  (invoiced)
├─ Installation: Vehicle ABC-123      0h    $0      (informative)
├─ Installation: Vehicle XYZ-789      0h    $0      (informative)
└─ Installation: Vehicle DEF-456      0h    $0      (informative)
                                    ----
Delivered: 3h / 50h
```

**Result in Project:**
```
📋 GPS Installations (Parent Task - 50h)
   ├─ 📌 Ticket #123 - Installation: Vehicle ABC-123 (1h) ✅ 1h logged
   ├─ 📌 Ticket #124 - Installation: Vehicle XYZ-789 (1h) ✅ 1h logged
   └─ 📌 Ticket #125 - Installation: Vehicle DEF-456 (1h) ⏳ 0h logged
```

---

## 🔧 Installation

### Prerequisites
- Odoo 18.0
- `helpdesk_task_upsell` module installed
- `helpdesk_fsm` module installed
- `sale_subscription` module installed

### Installation Steps

1. **Place the module** in your Odoo addons directory:
   ```bash
   /path/to/odoo/addons/helpdesk_task_upsell_advanced/
   ```

2. **Update apps list**:
   - Go to Apps menu
   - Click "Update Apps List"

3. **Install the module**:
   - Search for "Helpdesk Task Upsell Advanced"
   - Click "Install"

4. **Verify installation**:
   - Go to Helpdesk → Configuration → Upsell Category
   - You should see new fields: "Use Parent Task Hierarchy" and "Parent Product"

---

## ⚙️ Configuration

### Step 1: Create Parent Products

Create your parent products that will accumulate hours:

1. Go to **Sales → Products → Products**
2. Create product (e.g., "GPS Installations"):
   - **Product Type**: Service
   - **Invoicing Policy**: Based on Timesheets
   - **Create on Order**: Task (global project)
   - **Project**: Field Service Management
   - **Is a upsell**: ❌ No (this is a parent product)

### Step 2: Configure Upsell Categories

1. Go to **Helpdesk → Configuration → Upsell Category**
2. Create or edit a category:
   - **Name**: Installation
   - **Product**: (auto-created informative product)
   - **Use Parent Task Hierarchy**: ✅ Yes
   - **Parent Product**: GPS Installations

### Step 3: Use in Helpdesk Tickets

1. Open a helpdesk ticket
2. Click "Plan Intervention"
3. Check **"For Upsell"**
4. Fill in:
   - **Subscription**: Select customer's subscription order
   - **Upsell Category**: Select configured category
   - **Task Description**: Vehicle plate or operation identifier
   - **Quantity**: Hours for this operation
5. Click "Generate Task"

---

## 🔍 Technical Details

### Architecture

```
helpdesk_task_upsell (base)
         ↓
helpdesk_task_upsell_advanced (extension)
         ↓
    Extends:
    ├─ upsell.category (add fields)
    ├─ project.task (add helpers)
    └─ helpdesk.create.fsm.task (override logic)
```

### Key Methods

#### `action_generate_task()` Override
- Checks if `use_parent_task` is enabled
- If NO → delegates to base module (super call)
- If YES → executes advanced logic

#### Advanced Logic Flow
1. **Validate** fields and subscription state
2. **Get/Create** parent product line
3. **Get/Create** parent task
4. **Create** subtask with correct `parent_id` and `sale_line_id`
5. **Create** informative dummy line

### Database Schema Changes

**New Fields in `upsell.category`:**
```python
use_parent_task = Boolean
parent_product_id = Many2one('product.product')
```

**No new models created** - only extends existing ones.

---

## 🐛 Troubleshooting

### Issue: Parent task not found/created

**Check:**
- Parent product has `service_tracking = 'task_global_project'`
- Subscription order is in 'sale' state
- Project is configured in parent product

### Issue: Hours not accumulating

**Check:**
- Subtask has correct `sale_line_id` (should match parent task's)
- Timesheets are being logged on the subtask (not parent)
- Parent product line exists in subscription order

### Issue: Duplicate parent tasks

**Check:**
- Category configuration is correct
- `parent_product_id` is properly set
- Not mixing manual and automatic task creation

---

## 📊 Comparison: Before vs After

### Before (Base Module)
```
Order Line: Installation: ABC-123 → 1h → Task → Invoice $50
Order Line: Installation: XYZ-789 → 1h → Task → Invoice $50
Order Line: Installation: DEF-456 → 1h → Task → Invoice $50
Total: 3 separate invoices, hard to manage
```

### After (Advanced Module)
```
Parent Line: GPS Installations → 50h → Parent Task
├─ Subtask: Installation ABC-123 → 1h logged
├─ Subtask: Installation XYZ-789 → 1h logged  
└─ Subtask: Installation DEF-456 → 1h logged
Info Lines: Show details, don't invoice
Total: 1 invoice for 3h of 50h sold
```

---

## 🤝 Compatibility

- **Odoo Version**: 18.0
- **Dependencies**: `helpdesk_task_upsell`, `helpdesk_fsm`, `sale_subscription`
- **Backward Compatible**: ✅ Yes - can coexist with base module behavior

---

## 📝 License

LGPL-3

---

## 👥 Support

For issues, questions, or contributions:
- Check the troubleshooting section
- Review Odoo logs for detailed error messages
- Ensure all dependencies are properly installed

---

## 🔄 Version History

### v18.0.1.0.0 (Initial Release)
- Parent/child task hierarchy
- Dual product system
- Automatic parent detection
- Informative dummy lines
- Full backward compatibility