from selenium import webdriver
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import SQLFunctions as sql

def SelfHealing(driver, tasks, tasks_results, TestId):

    script = """
    function getCssAndXPath(element) {
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
        
        var elements = document.getElementsByTagName('*');
        var result = [];
        for (var i = 0; i < elements.length; i++) {
            var element = elements[i];
            result.push({
                tag_name: element.tagName.toLowerCase(),
                class: element.className || null,
                css_selector: getCssSelector(element),
                id: element.id || null,
                link_text: element.tagName.toLowerCase() === 'a' ? element.text : null,
                partial_link_text: element.tagName.toLowerCase() === 'a' ? element.text : null,
                name: element.name || null,
                xpath: getXPathForElement(element)
            });
        }
        return result;
    }
    return getCssAndXPath();
    """

    # Execute the JavaScript to get all element data
    data = driver.execute_script(script)
    driver.quit()

    page_data_df = pd.DataFrame(data)

    # Retrieve and format database data
    

    for result in tasks_results:
        if ('Inserted' not in result["Result"]) and ('Clicked' not in result["Result"]):

            action = result["action"]
            
            db_data_nonformatted = sql.getAllSuccessfulTasks(TestId, action)
            db_data = [
                {
                    "class": element.get("class", None),
                    "css_selector": element.get("css_selector", None),
                    "id": element.get("id", None),
                    "link_text": element.get("link_text", None),
                    "partial_link_text": element.get("partial_link_text", None),
                    "name": element.get("name", None),
                    "tag_name": element.get("tag_name", None),
                    "xpath": element.get("xpath", None)
                }
                for element in db_data_nonformatted
            ]
            db_data_df = pd.DataFrame(db_data)

            required_columns = ["class", "css_selector", "id", "link_text", "partial_link_text", "name", "tag_name", "xpath"]
            for col in required_columns:
                if col not in db_data_df.columns:
                    db_data_df[col] = 'None'

            # Fill NaN values and ensure consistent data types
            page_data_df.fillna('None', inplace=True)
            db_data_df.fillna('None', inplace=True)

            encoder = OneHotEncoder(handle_unknown='ignore')

            combined_data = pd.concat([page_data_df, db_data_df])

            combined_data = combined_data.astype(str)

            encoded_combined_data = encoder.fit_transform(combined_data)


            page_data_encoded = encoded_combined_data[:len(page_data_df)]
            db_data_encoded = encoded_combined_data[len(db_data_df):]

            step = result["Step"]

            current_element_data = {
                "class": None,
                "css_selector": None,
                "id": None,
                "link_text": None,
                "partial_link_text": None,
                "name": None,
                "tag_name": None,
                "xpath": None
            }
            current_element_data[tasks[step-1]['access']] = tasks[step-1]['selector']

            # Prepare the current element data for prediction
            df_current_element = pd.DataFrame([current_element_data])
            df_current_element.fillna("None", inplace=True)

            encoded_current_data = encoder.fit_transform(df_current_element)

            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            rf.fit(page_data_encoded, range(len(page_data_df)))

            predicted_index = rf.predict(encoded_current_data)[0]
            probabilities = rf.predict_proba(encoded_current_data)[0]

            print("Predicted element index: ", predicted_index)
            print("Probabilities: ")
            for i, p in enumerate(probabilities):
                if p > 0: # Filtering out zero probabilities for clarit,
                    print(f" Element {i} - Probability: {p}")

            print("Predicted element:")
            print(page_data_df.iloc[predicted_index])

            return

    

    

    # # Preprocessor and model pipeline
    # preprocessor = ColumnTransformer(
    #     transformers=[
    #         ("class", OneHotEncoder(handle_unknown='ignore'), ["class"]),
    #         ("css_selector", OneHotEncoder(handle_unknown='ignore'), ["css_selector"]),
    #         ("id", OneHotEncoder(handle_unknown='ignore'), ["id"]),
    #         ("link_text", OneHotEncoder(handle_unknown='ignore'), ["link_text"]),
    #         ("partial_link_text", OneHotEncoder(handle_unknown='ignore'), ["partial_link_text"]),
    #         ("name", OneHotEncoder(handle_unknown='ignore'), ["name"]),
    #         ("tag_name", OneHotEncoder(handle_unknown='ignore'), ["tag_name"]),
    #         ("xpath", OneHotEncoder(handle_unknown='ignore'), ["xpath"]),
    #     ]
    # )

    # rf_pipeline = Pipeline(steps=[
    #     ('preprocessor', preprocessor),
    #     ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    # ])

    # # Ensure training data has the required columns
    # X_train = db_data_df[required_columns]
    # y_train = np.arange(len(db_data_df))

    # # Fit the model
    # rf_pipeline.fit(X_train, y_train)

    

    #         df_current_element.to_csv('current.csv', index=False)

    #         # Transform the current element data using the preprocessor
    #         transformed_current_element = preprocessor.transform(df_current_element)

    #         # Predict the closest match and calculate probabilities
    #         predicted_index = rf_pipeline.named_steps['classifier'].predict(transformed_current_element)[0]
    #         probabilities = rf_pipeline.named_steps['classifier'].predict_proba(transformed_current_element)[0]

    #         # Get the most probable match from page_data_df
    #         most_probable_match = page_data_df.iloc[predicted_index]

    #         # Print probabilities for each element
    #         print("Predicted element index: ", predicted_index)
    #         print("Probabilities: ")
    #         for i, p in enumerate(probabilities):
    #             print(f" Element {i} - Probability: {p}")
    #             print(page_data_df.iloc[i])

    #         print("Predicted element:")
    #         print(most_probable_match.to_dict())

    #         return





    # # knn_pipeline.fit(X_train, y_train)

    # # for result in tasks_results:
    # #     if ('Inserted' or 'Clicked') not in result["Result"]:
    # #         step = result["Step"]

    # #         current_element_data = {
    # #             "class": None,
    # #             "css_selector": None,
    # #             "id": None,
    # #             "link_text": None,
    # #             "partial_link_text": None,
    # #             "name": None,
    # #             "tag_name": None,
    # #             "xpath": None
    # #         }

    # #         current_element_data[tasks[step]['access']] = tasks[step]['selector']
            
    # #         encoder = OneHotEncoder(handLe_unknown='ignore')

    # #         # Concatenate train and test data to ensure consistent encoding
    # #         combined_data = pd.concat([train_data.drop('id', axis=1), test_data.drop('id', axis=1)])

    # #         # Fit and transform the combined data
    # #         encoded_combined_data = encoder.fit_transform(combined_data)

    # #         # Split the encoded data back into train and test sets 
    # #         encoded_train_data = encoded_combined_data[:len(train_data)]
    # #         encoded_test_data = encoded_combined_data[len(train_data):]

    # #         # Initialize the RandomForestClassifier
    # #         rf = RandomForestClassifier(n_estimators=100, random_state=42)

    # #         # Fit the model on the training dalta using indices as labels
    # #         rf.fit(encoded_train_data, range(len(train_data)))

    # #         # Predict the index of the most likely element 
    # #         predicted_index = rf.predict(encoded_test_data)[0]
    # #         probabilities = rf.predict_proba(encoded_test_data)[0]

    # #         # Print the predicted element index and probabilities 
    # #         print("Predicted element index: ", predicted_index)
    # #         print("Probabilities: ")
    # #         for i, p in enumerate(probabilities):
    # #             if p > 0: # Filtering out zero probabilities for clarit,
    # #                 print(f" Element {1} - Probability: {p}")

    # #         print("Predicted element:")
    # #         print(train_data.iloc[predicted_index])

    # #         return 