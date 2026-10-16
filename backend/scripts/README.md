# Admin Bootstrap

## How to create the first admin

The BuildLearn platform does not expose admin registration through the public API or registration form. The first administrator must be created manually using the bootstrap script.

### Run the bootstrap script

```bash
cd backend
python -m scripts.create_admin
```

The script will prompt for:

- First name
- Last name
- Email
- Password

Passwords must be at least 8 characters long.

### Example session

```bash
$ python -m scripts.create_admin
BuildLearn — Admin Bootstrap
This creates the first administrator account.

First name: Jane
Last name: Doe
Email: jane@example.com
Password:
Admin account created successfully for jane@example.com.
```

### Login as admin

After running the script, log in through Swagger UI or the frontend `/login` page using the same email and password. The JWT will contain `role: admin`.

### Access the Admin frontend

Navigate to `/admin/dashboard`. The admin area is protected:

- Unauthenticated users are redirected to `/login`.
- Students and instructors are redirected to their own dashboards.
- Only users with `role: admin` can access the admin interface.

### Security notes

- The public registration endpoint `/auth/register` accepts only `student` and `instructor` roles.
- There is no public `/auth/register-admin` endpoint.
- Admin creation is a manual, offline bootstrap operation only.
