# Omah's Banking System

A command-line banking simulator written in Python. Supports account creation, PIN-secured login, deposits, withdrawals, transfers, transaction history, and a basic admin dashboard. Data is persisted to a local JSON file.

## Features

- **Account creation** — generates a random 9-digit account number and a PIN-protected account.
- **Secure PIN storage** — PINs are hashed with PBKDF2-HMAC-SHA256 (100,000 iterations) plus a random 16-byte salt; raw PINs are never stored.
- **Login with lockout** — 3 incorrect PIN attempts locks the account.
- **Deposits & withdrawals** — balance updates with input validation and attempt limits.
- **Transfers** — PIN-confirmed transfer between two existing accounts.
- **Transaction history** — every deposit, withdrawal, and transfer is logged with a timestamp.
- **Admin dashboard** — username/password-gated view of all accounts, a system summary, and the ability to unlock locked accounts.
- **Persistent storage** — all account data is saved to `bank_data.json` after every change.

## Requirements

- Python 3.x
- No external dependencies (uses only the standard library: `json`, `random`, `hashlib`, `os`, `datetime`)

## Usage

```bash
python banking_system.py
```

You'll see the main menu:

```
======================
OMAH'S BANKING SYSTEM
======================
1. Create Account
2. Login
3. Admin Dashboard
4. Exit
```

Enter a number or the matching word (e.g. `1` or `create`).

### Creating an account
You'll be asked for a name and a 4-digit PIN (entered twice to confirm). On success you'll get a generated account number — save it, you'll need it to log in.

### Logging in
Enter your account number and PIN. Three failed PIN attempts locks the account; a locked account must be unlocked by an admin.

Once logged in, the account menu offers:

```
1. Deposit
2. Withdraw
3. Transfer
4. Balance
5. Transactions
6. Logout
```

### Admin access
Default credentials (hardcoded in the script):

```
Username: admin
Password: admin123
```

From the dashboard you can list all accounts, see the total account count, or unlock a locked account by account number.

## Data storage

All account data lives in `bank_data.json` in the same directory as the script, structured as:

```json
{
  "123456789": {
    "name": "Jane Doe",
    "pin": "<salt+hash, hex-encoded>",
    "balance": 0.0,
    "transactions": [],
    "locked": false
  }
}
```

The file is created automatically on first run if it doesn't exist.

## Known issues / things to be aware of

- **Hardcoded admin credentials** — `admin` / `admin123` is in the source code. Fine for a demo, not safe for anything real; move this to an environment variable or config file before using it for more than learning purposes.
- **Hashing label is inaccurate** — a comment in the code calls this "bcrypt," but the implementation actually uses PBKDF2-HMAC-SHA256, which is a different (also reasonable) algorithm. Worth fixing the comment so it doesn't mislead future readers.
- **PINs stored in plaintext JSON, just hashed** — the hash itself is safe to store, but the whole `bank_data.json` file (balances, names, transaction history) is unencrypted on disk.
- **`transfer()` indentation bug** — the final `print("Too many invalid attempts.")` / `print("Transfer Cancelled")` lines sit outside the method body (at class level) due to indentation, so they never execute as part of a failed transfer and may cause issues at class-definition time depending on context.
- **No `requirements.txt` needed** — standard library only.
