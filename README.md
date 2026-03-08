# Password Generator

A Python password generator is a utility designed to create strong, unpredictable passwords to enhance online security.

These applications typically leverage Python’s built-in libraries to produce unique character strings that are resistant to brute-force attacks.

## Installation/Setup

```
git clone -b experiment <https://github.com/MyTeddyCodes/password_generator.git>  
```

run it within an environment like `conda`

```bash
pip install -r requirements.txt
```

## Web Interface

##### Home page

to run web interface run the below commands:

```
cd server
uvicorn app:app --reload
```
uvicorn will run the web page on http://127.0.0.1:8000/

![Example Web Homepage Image](./references/web_home_page)
![Example Web Homepage Image_2](./references/web_vault_image2)

##### Vault page

to save password or access vault you would be required to log in
![Example Web Vault Image](./references/web_vault_image)

## Command Line

```bash
python main.py
```

![Example Image 1](./references/reference_1)

<details>
  <summary>CLI Shorthand Command</summary>

##### CLI Shorthand

start by running:

```bash
python main.py 7

```

and provide the preferred length of password
run CLI shortcut by adding preferred password length in the CLI

![Example Image 2](./references/reference_2)

</details>
