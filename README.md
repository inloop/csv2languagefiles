# csv2languagefiles

Translates CSV containing language translations to both iOS and Android file formats.

## Features

* Both iOS and Android supported
* Multiple variants of apps supported, for whitelabel apps or just for multiple flavors
* Multilanguage support
* Possibility to designate certain keys for certain platforms or both
* Support for parameters in strings, {string}, {float}, {integer}
* Possible to include HTML tags in texts, values are correctly handled for platforms
* All translation files are also containing original (first) language values for better orientation
* Works just as charm

## Usage

You have to have python 2.7.x installed. No libraries apart from standard ones are not required.

```
python csv2languagefiles.py exported.csv
```

After this script finishes, you can find both iOS and Android generated language files in the directory where you ran the script.

## Example

The structure of CSV is basically self explanatory, and the format (column order, etc.) must be followed for the script to work corretly.

| Key                    | Variant | iOS | Android | en                                                              | sk                                                                     | 
|------------------------|---------|-----|---------|-----------------------------------------------------------------|------------------------------------------------------------------------| 
| user_with_name         |         | yes | yes     | User {string}                                                   | Užívateľ {string}                                                      | 
| user_with_name         | sales   | yes | yes     | Customer {string}                                               | Zákazník {string}                                                      | 
| welcome_message_styled |         |     | yes     | Welcome on our &lt;font style="color: red">red&lt;/font> website! | Vitajte na našej &lt;font style="color: red">červenej&lt;/font> stránke! | 

If this CSV is used as input, we get these files generated:

```
- android
 - src
  - main
   - res
    - values
     - strings.xml
    - values-en
     - strings.xml
    - values-sk
     - strings.xml
  - sales
   - res
    - values
     - strings.xml
    - values-en
     - strings.xml
    - values-sk
     - strings.xml
- ios
 - Localizableen.strings
 - Localizablesalesen.strings
 - Localizablesalessk.strings
 - Localizablesk.strings
```

Example of generated `ios/Localizablesalesen.Strings`:
```
/* Customer {string} */
"user_with_name" = "Customer %@";
```

Example of generated `android/src/main/res/values/strings.xml`:
```
<?xml version="1.0" encoding="utf-8"?>
<resources>

    <!-- User {string} -->
    <string name="user_with_name" formatted="false">User %s</string>

    <!-- Welcome on our <font style="color: red">red</font> website! -->
    <string name="welcome_message_styled"><![CDATA[ Welcome on our <font style="color: red">red</font> website!]]></string>
</resources>
```

# License

```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```