# Secondhand Marketplace

Upload of the **UseableSoftware** team project (UoB BUS45 coursework).

## Run locally

### Requirements
- Python 3.10+
- Dependencies:

```bash
pip install flask flask-sqlalchemy flask-wtf email-validator werkzeug pytest
```

### Start the server

From the project root:

```bash
python3 -c "from app import app; app.run(host='127.0.0.1', port=3000, debug=True)"
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000)

### Run tests

```bash
pytest -v
```

Tests use Flask's test client and a temporary SQLite database (they do not touch `instance/market.db`).

| File | Covers |
|------|--------|
| `tests/test_s1_upload_list.py` | Upload + list (S1) |
| `tests/test_s2_profile.py` | Password / edit / delete (S2) |
| `tests/test_s3_search.py` | Search + filters (S3) |

### Class Diagram

```mermaid
classDiagram
    class WebRouter {
        +upload()
        +market()
        +register()
        +login()
        +edit(String_id)
    }

    class ProductForm {
        +String_seller
        +String_name
        +String_category
        +Float_price
        +String_description
        +validate_on_submit()
    }

    class AuthForm {
        +String_username
        +String_password
        +String_email
        +validate_on_submit()
    }

    class MarketController {
        +get_all_products()
        +find_product_by_id(String_id)
    }

    class JsonScanner {
        +scan_directory()
        +parse_json_file(String_filename)
    }

    class StorageManager {
        -String_json_folder
        -String_seller_path
        +save_to_json(String_category,Dict_data)
        +save_user(Dict_data)
    }

    class User {
        +String_username
        +String_password
        +String_email
    }

    class Product {
        +String_id
        +String_seller
        +String_name
        +String_category
        +Float_price
        +String_image_path
    }

    WebRouter "1" --> "0..*" ProductForm : uses
    WebRouter "1" --> "0..*" AuthForm : uses
    WebRouter "1" --> "1" MarketController : delegates
    WebRouter "1" --> "1" StorageManager : requests_save
    MarketController "1" --> "1" JsonScanner : searches_with
    JsonScanner "1" --> "0..*" Product : finds
    StorageManager "1" --> "0..*" Product : stores
    StorageManager "1" --> "0..*" User : manages
    User "1" --> "0..*" Product : sells
```

### Use Case Diagram
```mermaid
flowchart LR
    %% Actors definition
    Guest((Guest))
    Member((Registered\nMember))

    %% System Boundary
    subgraph System [BUS45-Project Second-hand Market]
        direction TB
        
        %% Core Use Cases (Verb + Noun structure)
        UC_Reg([Register Account])
        UC_Login([Login to System])
        UC_Auth([Authenticate User])
        
        UC_Browse([Browse Market Products])
        UC_Search([Search & Filter Products])
        UC_View([View Product Details])
        
        UC_Upload([Upload Product])
        
        UC_ManageP([Manage Own Products])
        UC_Edit([Edit Product Details])
        UC_Delete([Delete Product])
        
        UC_Profile([Manage User Profile])
    end

    %% Actor Generalization
    %% Member inherits all behaviors of Guest
    Member -. "<<generalization>>" .-> Guest

    %% Guest Associations
    Guest --- UC_Reg
    Guest --- UC_Login
    Guest --- UC_Browse

    %% <<extend>> relationships (optional behavior, arrow points to base use case)
    UC_Search -. "<<extend>>" .-> UC_Browse
    UC_View -. "<<extend>>" .-> UC_Browse

    %% Member Associations
    Member --- UC_Upload
    Member --- UC_ManageP
    Member --- UC_Profile

    %% <<extend>> relationships for managing products
    UC_Edit -. "<<extend>>" .-> UC_ManageP
    UC_Delete -. "<<extend>>" .-> UC_ManageP

    %% <<include>> relationships (mandatory behavior, arrow points to included use case)
    UC_Upload -. "<<include>>" .-> UC_Auth
    UC_ManageP -. "<<include>>" .-> UC_Auth
    UC_Profile -. "<<include>>" .-> UC_Auth
    UC_Login -. "<<include>>" .-> UC_Auth

    %% Styling to mimic UML standard
    classDef actorStyle fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef ucStyle fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    
    class Guest,Member actorStyle;
    class UC_Reg,UC_Login,UC_Auth,UC_Browse,UC_Search,UC_View,UC_Upload,UC_ManageP,UC_Edit,UC_Delete,UC_Profile ucStyle;
```

### S1 Post Item - Sequence Diagram


```mermaid
sequenceDiagram
    autonumber

    actor User as :StudentSeller
    participant UI as browser :WebBrowser
    participant App as router :FlaskRoute
    participant Form as form :ProductForm
    participant Img as image :FileStorage
    participant FS as file_sys :JsonHandler

    Note over User, FS: Scenario: User uploads a new product via POST /upload

    User->>UI: clickSubmit(data, image)
    activate UI
    
    UI->>App: upload() [POST]
    activate App
    
    App->>Form: validate_on_submit()
    activate Form
    Form-->>App: return True
    deactivate Form

    Note right of App: Process Image
    App->>App: secure_filename(image.filename)
    App->>Img: save(image_path)
    activate Img
    Img-->>App: saved
    deactivate Img

    Note right of App: Process Data Logic
    App->>App: save_to_json(category, product)
    
    activate App
    App->>FS: open(json_path, 'r')
    activate FS
    FS-->>App: json.load(data)
    deactivate FS
    
    App->>App: data.append(product)

    App->>FS: open(json_path, 'w')
    activate FS
    FS-->>App: json.dump(data)
    deactivate FS
    deactivate App

    App-->>UI: redirect(url_for('market'))
    deactivate App

    UI->>UI: render('market.html')
    UI-->>User: displaySuccess()
    deactivate UI
```


### S2 User Profile - Sequence Diagram


```mermaid
sequenceDiagram
    autonumber

    participant U as User
    participant B as WebBrowser
    participant R as FlaskRoute (/dashboard)
    participant F as ProfileForm
    participant S as Session
    participant J as seller.json
    participant L as DashboardLogic
    participant T as TemplateEngine

    U->>B: Click Dashboard(userid)
    activate B
    B->>R: GET /dashboard/<userid>
    activate R

    R->>J: _load_sellers()
    activate J
    J-->>R: sellers list
    deactivate J

    R->>L: find seller by userid
    activate L
    L-->>R: dashboard_user
    deactivate L

    R->>S: get_current_user()
    activate S
    S-->>R: current_user
    deactivate S

    alt current_user.id == dashboard_user.id
        R->>F: validate_on_submit()
        activate F
        F-->>R: True
        deactivate F

        R->>L: check username uniqueness
        activate L
        L-->>R: OK
        deactivate L

        R->>J: update seller.json
        activate J
        J-->>R: updated
        deactivate J

        R->>L: update_products_seller_name()
        activate L
        L->>J: update product seller fields
        activate J
        J-->>L: updated
        deactivate J
        L-->>R: done
        deactivate L

        R->>S: update session username
        activate S
        S-->>R: updated
        deactivate S

        R-->>B: redirect /dashboard/<userid>
        deactivate R

        B->>R: GET /dashboard/<userid>
        activate R
    else
        R->>F: prefill form.username
        activate F
        F-->>R: filled
        deactivate F
    end

    R->>L: load_all_products()
    activate L
    L->>J: read all category json
    activate J
    J-->>L: product list
    deactivate J
    L-->>R: filtered user products
    deactivate L

    R->>T: render dashboard.html
    activate T
    T-->>B: Display Dashboard Page
    deactivate T

    deactivate R
    deactivate B
```


### S3 Search and Classification - Sequence diagram


```mermaid
sequenceDiagram
    autonumber
    actor Client as User (Browser)
    participant Controller as MarketController
    participant Scanner as JsonScanner
    participant FS as FileSystem

    Client->>Controller: GET /market
    activate Controller
    
    Controller->>Scanner: load_all_products()
    activate Scanner
    
    Scanner->>FS: os.listdir(JSON_FOLDER)
    activate FS
    FS-->>Scanner: List of filenames (e.g., ['books.json', 'electronics.json'])
    deactivate FS
    
    loop For each filename ending with '.json'
        Scanner->>FS: open(filename, 'r')
        activate FS
        FS-->>Scanner: File content (JSON string)
        deactivate FS
        
        Scanner->>Scanner: json.load(content) to List~Product~
        Scanner->>Scanner: append to all_products list
    end
    
    Scanner-->>Controller: Return complete all_products List
    deactivate Scanner
    
    Controller->>Controller: render_template('market.html', products=all_products)
    
    Controller-->>Client: Return HTML Response
    deactivate Controller
```
