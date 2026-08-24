# Access-Control Matrix

## Identity and role mapping

| Identity | Realm role | Intended access | Denied access | Principle |
|---|---|---|---|---|
| `observer` | `security-observer` | `/observer` | `/developer`, `/admin` | Read-only security observation. |
| `developer` | `developer` | `/developer` | `/observer`, `/admin` | Application development access. |
| `lab-admin` | `security-admin` | `/admin` | No denied route in this demonstration | Controlled administrative access. |

## Application authorization matrix

| Route | Required role | Observer | Developer | Lab admin |
|---|---|---:|---:|---:|
| `/` | Authenticated user | Allow | Allow | Allow |
| `/observer` | `security-observer` | Allow | Deny | Deny unless multiple roles are assigned |
| `/developer` | `developer` | Deny | Allow | Deny unless multiple roles are assigned |
| `/admin` | `security-admin` | Deny | Deny | Allow |
| `/logout` | Authenticated or anonymous | Allow | Allow | Allow |

## Validation sequence

1. Sign in as `observer` and confirm that `/observer` is allowed.
2. As `observer`, open `/developer` and confirm HTTP 403.
3. Sign out through the application and Keycloak.
4. Sign in as `developer` and confirm that `/developer` is allowed.
5. As `developer`, open `/observer` and confirm HTTP 403.
6. Create `lab-admin` in the `cloudsec` realm, assign `security-admin`, and confirm that `/admin` is allowed.

## Lifecycle controls

User access should be created only when required, assigned the minimum necessary role, reviewed periodically, and removed when the user no longer needs access. For this local lab, role removal or user disabling in Keycloak should be followed by a new login and a route-access test.

## Design decision

Authorization is enforced on the server using validated token claims. The user interface does not determine authorization; it only presents the result of the server-side decision.
