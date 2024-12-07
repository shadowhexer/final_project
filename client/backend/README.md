## It is recommended to run Django in a virtual environment

1. Create virtual environment
    ```
    py -m venv venv
    ```
 
2. Activate the virtual environment

    ```
    C:\path\to\your\final_project\client>venv\Scripts\activate
    ```

3. Install Dependencies

    ```
    (client)C:\path\to\your\final_project\client>pip install -r requirements.txt
    ```

4. Run the server
    ```
    (client)C:\path\to\your\final_project\client>py manage.py runserver
    ```

5. (Optional) You can automatically load the virtual environment when a folder with virtual env is opened to VS Code. Simply add `set DJANGO_SETTINGS_MODULE=<parent_folder_name>.settings` to the activate file in `\path\to\your\venv\Scripts\activate`. Replace the `<parent_folder_name>` to the name of the folder that houses the file (if you follow the steps above, simply replace it with `venv.settings`).

6. Contact me for the .env file