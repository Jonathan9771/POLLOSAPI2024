import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import socket
import requests
import SQLFunctions as sql
import SelfHealing as SH

def openWebPage(driver, url):
    try:
        driver.get(url)
        return "Web page opened successfully"
    except Exception as e:
        return f'Failed to open web page with url: "{url}"'
    
def TaskInsert(driver, steps, elements, response, etype):
    for step, element in zip(steps, elements):
        try:
            class_bd = element.get_attribute("class") or None
            css_script = """
                        function getCssSelector(element) {
                            if (element.tagName.toLowerCase() === 'html')
                                return 'html';
                            if (element.tagName.toLowerCase() === 'body')
                                return 'body';
                            var path = [];
                            while (element.parentNode) {
                                var siblings = element.parentNode.children;
                                var index = 0;
                                for (var i = 0; i < siblings.length; i++) {
                                    if (siblings[i] === element) {
                                        path.unshift(element.tagName.toLowerCase() + (index > 0 ? ':nth-of-type(' + (index + 1) + ')' : ''));
                                        break;
                                    }
                                    if (siblings[i].tagName === element.tagName)
                                        index++;
                                }
                                element = element.parentNode;
                            }
                            return path.join(' > ');
                        }

                        return getCssSelector(arguments[0]);
                    """
            css_selector = driver.execute_script(css_script, element)
            id = element.get_attribute("id") or None
            link_text = element.text if element.tag_name == "a" else None
            partial_link_text = element.text if element.tag_name == "a" else None
            name = element.get_attribute("name") or None
            tag_name = element.tag_name
            xpath_script = """
                        function getXPathForElement(element) {
                            var idx = function (sib) {
                                var count = 1;
                                for (var sibling = sib.previousSibling; sibling; sibling = sibling.previousSibling) {
                                    if (sibling.nodeType === 1 && sibling.nodeName === sib.nodeName) {
                                        count++;
                                    }
                                }
                                return count;
                            };
                            var segs = [];
                            for (; element && element.nodeType === 1; element = element.parentNode) {
                                if (element.hasAttribute('id')) {
                                    segs.unshift(element.localName.toLowerCase() + '[@id="' + element.getAttribute('id') + '"]');
                                } else {
                                    var index = idx(element);
                                    var tagName = element.localName.toLowerCase();
                                    segs.unshift(tagName + '[' + index + ']');
                                }
                            }
                            return segs.length ? '/' + segs.join('/') : null;
                        }

                        return getXPathForElement(arguments[0]);
                    """
            
            xpath = driver.execute_script(xpath_script, element)

        except: 
            class_bd = None
            css_selector = None
            id = None
            link_text = None
            partial_link_text = None
            name = None
            tag_name = None
            xpath = None

        action = step['action']
        access = step['access']
        quantity = step['quantity']
        selector = step['selector']
        try:
            text = step['text']
        except:
            text = None

        try:
            position = step['position']
        except:
            position = None

        if(etype == 'Success'):
            success_id = response["id"]
            error_id = None
        else:
            success_id = None
            error_id = response["id"]

        sql.insertTask(class_bd, css_selector, id, link_text, partial_link_text, name, tag_name, xpath, action, access, quantity, selector, text, position, success_id, error_id)
        

def getElement(driver, access, quantity, selector):
    try:
        match access, quantity:
            case "class", "singular":
                element = driver.find_element(By.CLASS_NAME, selector)
            case "class", "multiple":
                element = driver.find_elements(By.CLASS_NAME, selector)
            case "css_selector", "singular":
                element = driver.find_element(By.CSS_SELECTOR, selector)
            case "css_selector", "multiple":
                element = driver.find_elements(By.CSS_SELECTOR, selector)
            case "id", "singular":
                element = driver.find_element(By.ID, selector)
            case "id", "multiple":
                element = driver.find_elements(By.ID, selector)
            case "link_text", "singular":
                element = driver.find_element(By.LINK_TEXT, selector)
            case "link_text", "multiple":
                element = driver.find_elements(By.LINK_TEXT, selector)
            case "partial_link_text", "singular":
                element = driver.find_element(By.PARTIAL_LINK_TEXT, selector)
            case "partial_link_text", "multiple":
                element = driver.find_elements(By.PARTIAL_LINK_TEXT, selector)
            case "name", "singular":
                element = driver.find_element(By.NAME, selector)
            case "name", "multiple":
                element = driver.find_elements(By.NAME, selector)
            case "tag_name", "singular":
                element = driver.find_element(By.TAG_NAME, selector)
            case "tag_name", "multiple":
                element = driver.find_elements(By.TAG_NAME, selector)
            case "xpath", "singular":
                element = driver.find_element(By.XPATH, selector)
            case "xpath", "multiple":
                element = driver.find_elements(By.XPATH, selector)
            case _:
                if(quantity != "singular" or quantity != "multiple"):
                    raise ValueError(f'Unknown quantity input: "{quantity}"')
                else:
                    raise ValueError(f'"Unknown access type: "{access}"')
                
        return element
    except Exception as e:
        raise ValueError(f'Failed to find element with {access}: "{selector}"')


def addText(driver, access, quantity, selector, text, positionstring, elements):
    try:
        result = f'Inserted text "{text}" with {access}: "{selector}"'
        textFieldBase = getElement(driver, access, quantity, selector)
        if(quantity == "singular"):
            textField = textFieldBase
        elif(quantity == "multiple"):
            try:
                position = int(positionstring)
                if(position >= 0):
                    try:
                        textField = textFieldBase[position]
                        result = result + f' on position [{position}]'
                    except IndexError:
                        raise ValueError(f'There is no element with {access}: "{selector}" on position: [{position}]')
                else:
                    raise ValueError(f"Incorrect position input: [{position}], must be a positive digit")
            except TypeError:
                raise ValueError(f'Incorrect position input: "{positionstring}", must be a digit') ##############################################################
        else:
            raise ValueError(f'Incorrect quantity input: "{quantity}"')
        textField.clear()
        textField.send_keys(text)
        elements.append(textField)
        return result
    except Exception as e:
        print(e)
        elements.append(None)
        return f"{e}" 

def clickElement(driver, access, quantity, selector, positionstring, elements):
    try:
        result = f'Clicked element with {access}: "{selector}"'
        linkBase = getElement(driver, access, quantity, selector)
        if(quantity == "singular"):
            link = linkBase
        elif(quantity == "multiple"):
            try: 
                position = int(positionstring)
                if(position >= 0):
                    try:
                        link = linkBase[position]
                        result = result + f' on position [{position}]'
                    except IndexError:
                        raise ValueError(f'There is no element with {access}: "{selector}" on position: [{position}]')
                else:
                    raise ValueError(f"Incorrect position input: [{position}], must be a positive digit")
            except (TypeError):
                raise ValueError(f'Incorrect position input: "{positionstring}", must be a digit') ##############################################################
        else:
            raise ValueError(f'Incorrect quantity input: "{quantity}"')
        link.click()
        elements.append(link)
        return result
    except Exception as e:
        print(e)
        elements.append(None)
        return f"{e}" 
    
def closeBrowser(driver):
    try:
        driver.quit()
        return "Browser closed successfully"
    except Exception as e:
        return f"Failed to close browser"
    
def execute_steps(driver, steps, elements):
    results = []
    for step in steps:
        action = step.get('action')
        access = step.get('access')
        quantity = step.get('quantity')
        selector = step.get('selector')
        text = step.get('text')
        position = step.get('position')
        
        if action == 'add_text':
            result = addText(driver, access, quantity, selector, text, position, elements)
        elif action == 'click_element':
            result = clickElement(driver, access, quantity, selector, position, elements)
        else:
            result = f"Unknown action: {action}"
        results.append(result)
    return results

def testing(url, ip, steps):
    
    # Enviar los resultados a la API Flask
    test_data = {
        "IP": ip,
        "Webpage": url,
        "Browser": "Chrome"
    }
    if test_data["IP"] is None:
        raise ValueError("IP is None")
    elif test_data["Webpage"] is None:
        raise ValueError("Webpage is None")
    
    # Si ya se encuentra en la BD, no se inserta
    testId = test_data["IP"] + ":" + test_data["Webpage"]
    test = sql.getTestById(testId)

    if(len(test) == 0):
        response = sql.insertTest(testId ,test_data["Webpage"], test_data["Browser"])
        if response:
            print("Error al insertar el test en la base de datos.")

    driver = webdriver.Chrome()  # Cambia esto dependiendo del navegador que estés utilizando

    # Abrir la página web
    result = openWebPage(driver, url)
    if 'successfully' not in result:
        print(result)
        driver.quit()
        exit()

    driver.implicitly_wait(10)

    elements = []
    
    results = execute_steps(driver, steps, elements)
    print("Results:", results)
    
    if all(('Inserted' or 'Clicked') in step_result for step_result in results):
        etype = "Success"
    else:
        etype = next((result for result in results if ('Inserted' or 'Clicked') not in result), "Success")
        etype = etype[:200]
        
    test_data["EType"] = etype
    test_data["TestId"] = testId
    
    stepslist = []
    for idx, result in enumerate(results, start=1):
        step_data = {
            "Step": idx,
            "Result": result
        }
        stepslist.append(step_data)

    # Extraer la información relevante de cada diccionario
    formatted_steps = [f"Step {step['Step']}: {step['Result']}" for step in stepslist]

    # Unir los pasos en una cadena con saltos de línea como separador
    allSteps = "\n".join(formatted_steps)
    test_data["Steps"] = allSteps

    # response = requests.post(f"http://127.0.0.1:5000/insert{'Success' if etype == 'Success' else 'Error'}", json=test_data)
    if(etype == 'Success'):
        response = sql.insertSuccess(test_data["TestId"], test_data["Steps"])
    else:
        response = sql.insertError(test_data["TestId"], test_data["EType"], test_data["Steps"])

    if response == None:
        print(f"Error al insertar el {'success' if etype == 'Success' else 'error'} en la base de datos.")
    else:
        TaskInsert(driver, steps, elements, response, etype)

    if(etype != 'Success'):
        SH.SelfHealing(driver, steps, stepslist, testId)
    else:
        driver.quit()

    driver.quit()

    if(etype == 'Success'):
        return test_data, True
    
    else:
        return test_data, False