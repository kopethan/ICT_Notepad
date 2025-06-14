## 📦 Database Structure Summary

Here’s how your SQLAlchemy database is structured (`models.py`):

### 1. `PDArray`

| Field   | Type     | Notes                     |
| ------- | -------- | ------------------------- |
| id      | Integer  | Primary Key               |
| name    | String   | Unique name of the array  |
| session | String   | e.g., "London", "NY"      |
| date    | Date     | Automatically set         |
| notes   | Text     | Optional                  |
| color   | String   | Hex code                  |
| levels  | Relation | → has many `Level`        |
| tags    | Relation | → many-to-many with `Tag` |

---

### 2. `Level`

| Field         | Type     | Notes                      |
| ------------- | -------- | -------------------------- |
| id            | Integer  | Primary Key                |
| pd\_array\_id | FK       | → `PDArray.id`             |
| level\_type   | String   | e.g., "POI", "Liquidity"   |
| value         | String   | Can be price or time       |
| timeframe     | String   | e.g., "1h", "15m"          |
| label         | String   | e.g., "High", "CE", "0.75" |
| notes         | Text     | Optional                   |
| entries       | Relation | → has many `LevelEntry`    |

---

### 3. `LevelEntry`

| Field     | Type     | Notes                         |
| --------- | -------- | ----------------------------- |
| id        | Integer  | Primary Key                   |
| level\_id | FK       | → `Level.id`                  |
| value     | String   | User-input value (price/time) |
| note      | Text     | Optional notes                |
| timestamp | DateTime | Automatically set on creation |

---

### 4. `Tag`

| Field      | Type     | Notes                       |
| ---------- | -------- | --------------------------- |
| id         | Integer  | Primary Key                 |
| name       | String   | Unique name                 |
| pd\_arrays | Relation | many-to-many with `PDArray` |

---

### 5. `AppSetting` (optional use for config)

| Field | Type    | Notes                   |
| ----- | ------- | ----------------------- |
| id    | Integer | Primary Key             |
| key   | String  | e.g. "default\_session" |
| value | String  | Stored setting          |

---