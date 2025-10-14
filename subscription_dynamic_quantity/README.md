# Subscription Dynamic Quantity

Automatically adjust subscription quantities based on service deliveries (installations/uninstallations).

## Features

- Link installation/uninstallation products to subscription products
- Automatic subscription line creation in sales orders
- Dynamic quantity calculation: Installations - Uninstallations
- Protection against negative quantities (auto-adjust to 0)
- Visual warnings and detailed notifications

## Installation

1. Copy module to addons folder
2. Update Apps list
3. Install "Subscription Dynamic Quantity"

## Configuration

1. Create subscription product (with recurring invoice enabled)
2. Create installation/uninstallation service products
3. Link service products to subscription product
4. Define service type (Installation/Uninstallation)

## Usage

When you add installation/uninstallation products to a sale order, the subscription line is automatically added and its quantity calculated based on deliveries.