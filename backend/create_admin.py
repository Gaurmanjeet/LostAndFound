from getpass import getpass

from werkzeug.security import generate_password_hash

from database import get_db_connection


def create_admin():

    print("\n==============================")
    print("   LOST & FOUND ADMIN SETUP")
    print("==============================\n")


    full_name = input("Admin name: ").strip()

    email = input("Admin email: ").strip().lower()

    password = getpass("Admin password: ")

    confirm_password = getpass(
        "Confirm password: "
    )


    # ---------------------------------------------
    # VALIDATION
    # ---------------------------------------------

    if not full_name:
        print("\n❌ Admin name is required.")
        return


    if not email:
        print("\n❌ Admin email is required.")
        return


    if len(password) < 6:
        print("\n❌ Password must be at least 6 characters.")
        return


    if password != confirm_password:
        print("\n❌ Passwords do not match.")
        return


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        # -----------------------------------------
        # CHECK EXISTING EMAIL
        # -----------------------------------------

        cursor.execute(
            """
            SELECT id, role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )


        existing_user = cursor.fetchone()


        if existing_user:

            print(
                "\n❌ This email is already registered."
            )

            print(
                f"Existing user ID: {existing_user[0]}"
            )

            print(
                f"Existing role: {existing_user[1]}"
            )

            return


        # -----------------------------------------
        # HASH PASSWORD
        # -----------------------------------------

        password_hash = generate_password_hash(
            password
        )


        # -----------------------------------------
        # CREATE ADMIN
        # -----------------------------------------

        cursor.execute(
            """
            INSERT INTO users
            (
                full_name,
                email,
                password_hash,
                role
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'admin'
            )
            """,
            (
                full_name,
                email,
                password_hash
            )
        )


        connection.commit()


        print("\n================================")
        print("✅ ADMIN ACCOUNT CREATED")
        print("================================")

        print(f"Name  : {full_name}")
        print(f"Email : {email}")
        print("Role  : admin")

        print(
            "\nYou can now login using this email"
            " and the password you entered."
        )


    except Exception as error:

        if connection:
            connection.rollback()

        print(
            f"\n❌ Error creating admin: {error}"
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    create_admin()