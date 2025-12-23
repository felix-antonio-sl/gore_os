# IFML in a Nutshell

## Introduction

### 1.1. What IFML is About

IFML supports the specification of the front end of applications independently of the technological details of their realization. It addresses the following questions of front-end modeling:
- The composition of the view: What are the visualization units that compose the interface, how are they organized, and which ones are displayed simultaneously and which in mutual exclusion?
- The content of the view: What content elements are displayed from the application to the user, and what input is acquired from the user and supplied to the application?
- The commands: What interaction events are supported?
- The actions: What business components are triggered by the events?
- The effects of interaction: What is the effect of events and action execution on the state of the interface?
- The parameter binding: What data items are communicated between the elements of the user interface and the triggered actions?

IFML expresses the abovementioned aspects using a visual modeling language based on the OMG standards. Its technical foundations lie on the OMG Model Driven Architecture (MDA) framework. This grants seamless integration with the specifications of the other layers of the software system. The specification consists of five main technical artifacts:
- The IFML metamodel specifies the structure and semantics of the IFML constructs using the OMG Meta Object Facility (MOF).
- The IFML Unified Modeling Language (UML) profile defines a UML-based syntax for expressing IFML models. In particular, the UML Profile for IFML is based on the use of UML components (both basic components and packaging components), classes, and other concepts, which may concur with hierarchical structures or dependencies.
- The IFML visual syntax offers a concrete representation based on a unique diagram. This compacts all aspects of the user interface that are otherwise expressed separately with UML class diagrams, state machine, and composite structure diagrams.
- The IFML textual syntax offers a textual alternative, equivalent to the visual syntax, for expressing IFML models.
- The IFML XMI provides a model exchange format for tool portability.

This book adopts the IFML visual syntax as a concrete vehicle for conveying the user interaction models because it is close to UML—and thus familiar to developers—and because it is very compact.

### 1.2. The IFML Design Principles

Designing a modeling language for the front end is a complex and multidisciplinary task where many perspectives intersect. A good modeling language should pay attention to coverage (i.e., the ability to represent complex application front ends but also to model usability and understandability). The latter goals require addressing all the factors that contribute to make a modeling language quick to learn, simple to use, easy to implement by tool vendors, and open to extensibility. The design of IFML adheres as much as possible to the following “golden” rules:
- Conciseness: the number of diagram types and concepts needed to express the salient interface and interaction design decisions is kept to the minimum. In particular, the IFML visual syntax conveys the front-end model using a single diagram. This design simplifies the model editing and maintenance processes, because references between different types of diagrams need not be maintained and only the internal coherence among the various elements of a single type of diagram must be preserved.
- Inference from the context: whenever something can be deduced from existing parts of the model, inference rules at the modeling level automatically apply default modeling patterns and details, avoiding the need for modelers to specify redundant information. For example, parameter passing rules between different model elements, which are ubiquitous and cumbersome to specify, are inferred from the context as often as possible.
- Extensibility: adaptation to novel requirements, interaction modalities, and technologies must be planned in the language design. IFML builds upon a small set of core concepts that capture the essence of interaction: the interface (containers), stimuli (events), content (components and data binding), and dynamics (flows and actions). By design, these concepts are meant to be extended to mirror the evolution of technologies and devices. Thus, IFML incorporates standard means for defining new concepts, such as novel interface components or event types. The OMG standard already comprises examples of extensions, and this book illustrates many more cases that ease the specification of web, desktop, and mobile applications. Time and practice will show if the core of IFML is sufficiently technology neutral to enable extension to novel interaction paradigms that are possibly very different from the ones for which the language was initially conceived.
- Implementability: models that lack adequate tool support and cannot be used to produce the code are quickly abandoned. IFML is a platform-independent language but has been designed with executability in mind. This is obtained through model transformations and code generators to ensure that models can be mapped easily into executable applications for various platforms and devices. Chapters 10 and 11 present some techniques for implementing IFML specifications in several platforms, discuss the tool support requested in general for making the language usable, and illustrate one specific tool that enables automation of the design process and code generation.
- Not everything in the model: sometimes the hardest choice in language design is what to leave out. IFML purposely ignores presentation aspects, because presentation is adversarial to abstraction (in graphic design, every pixel is important). It also delegates to external models the specification of aspects that, although relevant to the user interface, are not properly part of it. For example, the internal functioning of the actions triggered by the GUI can be described using an action model. If the action is the invocation of an object’s method, this can be described by referencing a method in a UML class; if the action is the invocation of an orchestration of web services, this can be described using a SoaML1 diagram; if the action is described by a complex behavior, this can be obtained by referencing a whole UML dynamic diagram (e.g., a sequence diagram or activity diagram). The content model underlying the application can be described with any structural diagram, such as a UML class diagram, a Common Warehouse Metamodel (CWM) diagram,2 an Entity-Relationship diagram, or an ontology.

## IFML in a Nutshell

To understand the aim and scope of IFML better, it may be useful to refer to the well-known Model–View–Controller (MVC) software architecture of an interactive application,1 shown in Figure 2.1. MVC distinguishes the application’s internal status and business logic (Model), their representation in the user interface (View), and the rules governing the response to the user’s interaction (Controller).

IFML mainly describes the view (i.e., the content of the front end and the user interaction mechanisms available in the interface). More precisely, IFML covers various aspects of the user interface:
- View structure: It expresses the general organization of the interface in terms of ViewContainers, along with their nesting relationships, visibility, and reachability.
- View content: It specifies what ViewContainers actually contain in terms of ViewComponents (i.e., elements for content display and data entry). ViewComponents that display content are further characterized by a ContentBinding, which expresses the source of the published content.
- Events: They are the occurrences that affect the state of the user interface. They can be produced by a user’s interaction, by the application itself, or by an external system.
- Event transitions: They specify the consequences of an event on the user interface, which can be a change of the ViewContainer, an update of the content on display, the triggering of an action, or a mixture of these effects.
- Parameter binding: It clarifies the input–output dependencies between ViewComponents, view containers, and actions.

For the sake of conciseness, IFML condenses all these perspectives within only one diagram type called an Interaction Flow Diagram. This is in contrast to other modeling languages such as UML, which rely on multiple diagrams for conveying the various facets of an application.

Besides describing the view part of the application, an IFML Interaction Flow Diagram also provides the hooks to connect it with the model and controller parts:
- With respect to the controller, IFML represents the effects of the user’s interactions. It defines the events produced in the view and the course of action taken by the controller in response to them, such as triggering a business component and updating the view.
- With respect to the model, IFML describes the data binding between the interface elements and the objects that embody the state of the application, as well the actions that are triggered by the user’s interactions.

Figure 2.2 shows as an initial example the IFML model of a simple interface: the view structure consists of three ViewContainers (“ProductCategories,” “ProductOfCategory,” and “ProductInformation”), which reflect the top-level organization of the GUI in three distinct pages. The model shows the content of each ViewContainer. For example, the “ProductCategories” ViewContainer comprises one ViewComponent called “CategoryList.” This notation represents the content of the respective page in the GUI (i.e., a list of product categories). Events are represented in IFML as circles. The “SelectCategory” event specifies that the “CategoryList” component is interactive. In the GUI, the user can select one of the categories to access a list of its products. The effect of the “SelectCategory” event is represented by the arrow emanating from it (called InteractionFlow in IFML), which specifies that the triggering of the event causes the display of the “ProductOfCategory” ViewContainer and the rendering of its “ProductList” ViewComponent (i.e., the list of products of the selected category). The input–output dependency between the “CategoryList” and the “ProductList” ViewComponents is represented as a parameter binding (the IFML ParameterBindingGroup element in Figure 2.2). The value of the “SelectedCategory” parameter, which denotes the object selected by the user in the “CategoryList” ViewComponent, is associated with the value of the input parameter “Category,” which is requested for the computation of the “ProductList” ViewComponent.

### Overview of IFML Main Concepts

An IFML diagram consists of one or more top-level ViewContainers (i.e., interface elements that comprise components for displaying content and supporting interactions).

Figure 2.3 contrasts two different organizations of the GUI: (a) an e-mail application (desktop or rich Internet application) consisting of a top-level container with embedded sub-containers at different levels, and (b) an e-commerce web site that organizes the user interface into different independent view containers corresponding to page templates.

Each view container can be internally structured in a hierarchy of subcontainers. For example, in a desktop or rich Internet application, the main window can contain multiple tabbed frames, which in turn may contain several nested panes. The child view containers nested within a parent view container can be displayed simultaneously (e.g., an object pane and a property pane) or in mutual exclusion (e.g., two alternative tabs). In the case of mutually exclusive (XOR) containers, one could be the default container, which is displayed by default when the parent container is accessed. The meaning of a container can be specified more precisely by adding a stereotype to the general-purpose construct. For instance, a ViewContainer can be tagged as «window», as in the case of the “Mail” ViewContainer in Figure 2.4, to hint at the nature of its expected implementation.

In Figure 2.4, the “Mail” top-level container comprises two subcontainers, displayed alternatively: one for messages and one for contacts. When the top level container is accessed, the interface displays the “Messages” ViewContainer by default.

A ViewContainer can contain ViewComponents, which denote the publication of content (e.g., a list of objects) or the input of data (e.g., entry forms).

Figure 2.5 shows the notation for embedding ViewComponents within ViewContainers. The “Search” ViewContainer comprises a “MessageKeywordSearch” ViewComponent that represents a form for searching; the “MailBox” ViewContainer comprises a “MessageList” ViewComponent that denotes a list of objects.

A ViewComponent can have input and output parameters. For example, a ViewComponent that shows the details of an object has an input parameter corresponding to the identifier of the object to display. a data entry form exposes as output parameters the values submitted by the user. and a list of items exports as output parameter the item selected by the user.

A ViewContainer and a ViewComponent can be associated with events to express that they support user interaction. For example, a ViewComponent can represent a list associated with an event for selecting one or more items, a form associated with an event for input submission, or an image gallery associated with an event for scrolling though the gallery. IFML events are mapped to interactors2 in the implemented application. The way in which such interactors are rendered depends on the specific platform for which the application is deployed and is not captured by IFML. Rather, it is delegated to transformation rules from a platform-independent model (PIM) to a platform-specific model (PSM). For example, the scrolling of an image gallery may be implemented as a link in an HTML application and as a swipe gesture handler in a mobile phone application.

The effect of an event is represented by an interaction flow, which connects the event to the ViewContainer or ViewComponent affected by the event. For example, in an HTML web application the event produced by the selection of one item from a list may cause the display of a new page with the details of the selected object. This effect is represented by an interaction flow connecting the event associated with the list component in a top-level ViewContainer (the web page) with the ViewComponent representing the object detail, which is positioned in a different ViewContainer (the target web page). The interaction flow expresses a change of state of the user interface. The occurrence of the event causes a transition from a source to a target web page.

For example, in Figure 2.6 the “MailBoxList” ViewComponent shows the list of available mailboxes and is associated with the “MailBoxSelection” event, whereby the user can open the “MailBox” ViewContainer and access the messages of the mailbox selected in the “MessageList” ViewComponent .

An event can also cause the triggering of an action, which is executed prior to updating the state of the user interface. The effect of an event firing an action is represented by an interaction flow connecting the event to an action symbol (represented by a hexagon). For example, in a mail management application, the user can select several messages from a list and choose to delete them. The selection event triggers a delete action, after which the ViewContainer is displayed again with an updated list. The result of action execution is represented by an interaction flow that connects the action to the affected ViewContainer or ViewComponent.

In Figure 2.7, the “Message toolbar” ViewContainer is associated with the events for deleting, archiving, and reporting mail messages. Such events are connected by a flow to an action symbol (a labeled hexagonal icon), which represents the business operation. The outgoing flow of the action points to the ViewContainer displayed after the action is executed; if the outgoing flow of an action is omitted, this means that the same ViewContainer from which the action was activated remains in view (as illustrated by the “Archive” and “Report” actions in Figure 2.7).

The model of Figure 2.7 does not express the objects on which the business actions operate. Such an input–output dependency between view elements (ViewContainers and ViewComponents) or between view elements and actions requires the specification of parameter bindings associated with interaction flows. More specifically, two kinds of interaction flows can host parameter bindings: navigation flows, which represent navigation between view elements, and data flows, which express data transfer only but are not produced by user interaction. Parameter binding rules are represented by annotations attached to navigation and data flows, as shown in Figure 2.8.

In Figure 2.7, the “MessageToolbar” ViewContainer has an input parameter “MessageSet” whose value is set to the messages selected from the “MessageList” ViewComponent when the user triggers the “MessageSelection” event. Another parameter binding rule is associated with the Delete, Archive and Report events; the value of the “MessageSet” parameter is bound to the “InputMessages” parameter of the triggered action.

### Role of IFML in the Development Process

The development of interactive applications is typically managed with agile approaches, which traverse several cycles of “problem discovery” / “design refinement” / “implementation.” Each iteration of the development process generates a prototype or a partial version of the system. Such an incremental lifecycle is particularly appropriate for modern web and mobile applications, which must be deployed quickly and change frequently during their lifetime to adapt to user requirements. Figure 2.9 schematizes a possible development process and positions IFML within the flow of activities.

Requirements specification collects and formalizes the information about the application domain and expected functions. The input is the set of business requirements that motivate the application development and all the available information on the technical, organizational, and managerial context. The output is a functional specifications document comprising:
- the identification of the user roles and of the use cases associated with each role;
- a data dictionary of the essential domain concepts and of their semantic relationships; and
- the workflow embodied in each use case, which shows how the main actors (the user, the application, and possibly external services) interact during the execution of the use case.

In addition, nonfunctional requirements must also be specified, including performance, scalability, availability, security, and maintainability. When the application is directed to the general public, requirements about the look and feel and the usability of the interfaces assume special prominence among the nonfunctional requirements. User-centered design practices that rely on the construction of realistic mock-ups of the application functionality can be applied. These mock-ups can be used for the early validation of the interface concepts and then serve as the basis for creating more detailed and technical specifications during the front-end modeling phase.

Domain modeling3 organizes the main information objects identified during requirements specification into a comprehensive and coherent domain model. Domain modeling specifies the main information assets identified during requirements specification into a domain model, which is a (typically visual) representation of the essential objects, their attributes and associations. The first conceptual data modeling language, the Entity-Relationship model, was proposed in 1976, and ever since new modeling languages have been proposed, including UML. At the same time, modeling practices and guidelines have been consolidated; in particular, domain modeling for interactive applications exploits suitable design patterns, discussed in chapter 3. The entities and associations of the domain model identified during domain modeling are referenced in the front-end design models, to describe what pieces of data are published in the interface.

Front-end modeling maps the information delivery and data manipulation functionality dictated by the requirements use cases into a front-end model. Front-end modeling operates at the conceptual level, where IFML comes into play. The designer may use IFML to specify the organization of the front end in one or more top-level view containers, the internal structure of each view container in terms of subcontainers, the components that form the content of each view container, the events exposed by the view containers and components, and how such events trigger business actions and update the interface.

Business logic modeling specifies the business objects and the methods necessary to support the identified use cases. UML static and dynamic diagrams are normally employed to highlight the interfaces of objects and the flow of messages. Process-oriented notations—such as UML activity and sequence diagrams, BPMN process models, and BPEL service orchestrations—provide a convenient way to represent the workflow across objects and services. The actions specified in the business logic design can be referenced in the front-end model to show which operations can be triggered by interacting with the interface.

Data, front-end, and business-logic design are interdependent activities executed iteratively. The precedence order of Figure 2.9 is only illustrative. In some organizations, work could start from the design of the front end and the data objects and actions could be discovered at a later stage by analyzing what information is published in the interface and what operations are requested to support the interactions.

Architecture design is the process of defining the hardware, network, and software components that make up the architecture on which the application delivers its services to users. The goal of architecture design is to find the mix of these components that best meets the application requirements in terms of performance, security, availability, and scalability, and at the same time respects the technical and economic constraints of the project. The inputs of architecture design are the nonfunctional requirements and the constraints identified during business requirements collection and formalized in the requirements specifications. The output may be any specification that addresses the topology of the architecture in terms of processors, processes, and connections, such as UML deployment diagrams.

Implementation is the activity of producing the software modules that transform the data, business logic, and interface design into an application running on the selected architecture. Data implementation maps the domain model onto one or more data sources by associating the conceptual-level constructs with the logical data structures (e.g., entities and relationships to relational tables). Business logic implementation creates the software components needed to support the identified use cases. The implementation of individual components may benefit from the adoption of software frameworks, which organize the way in which fine-grain components are orchestrated and assembled into larger and more reusable functional units and also cater to nonfunctional requirements like performance, scalability, security, and availability. Business logic may also reside in external services, in which case implementation must address the orchestration of calls to remote components such as web APIs (Application Programming Interfaces). Interface implementation translates the conceptual-level ViewContainers and ViewComponents into the proper constructs in the selected implementation platform. ViewContainers may interoperate with business objects deployed either in the client layer or in the server layer.

Testing and evaluation verify the conformance of the implemented application to the functional and nonfunctional requirements. The most relevant concerns for interactive applications testing are:
- Functional testing: the application behavior is verified with respect to the functional requirements. Functional testing can be broken down into the classical activities of module testing, integration testing, and system testing.
- Usability testing: the nonfunctional requirements of ease of use, communication effectiveness, and adherence to consolidated usability standards are verified against the produced front end.
- Performance testing: the throughput and response time of the application must be evaluated in average and peak workload conditions. In case of inadequate level of service, the deployment architecture, including the external services, must be monitored and analyzed to identify and remove bottlenecks.

Deployment is the activity of installing the developed modules on top of the selected architecture. Deployment involves the data layer, the software gateways to the external services, and the business and presentation layer, where the interface modules and the business objects must be installed.

Maintenance and evolution encompass all the modifications applied after the application has been deployed in the production environment. Differently from the other phases of development, maintenance and evolution are applied to an existing system, which includes both the running application and its related documentation.

IFML models are the result of front-end design, but their production has important implications for other development activities as well.
- Domain modeling may specify entities and associations whose purpose is to aid the categorization and retrieval of the main business objects for a better user experience. We discuss this practice in chapter 3.
- Business logic modeling identifies the available operations and defines their possible outcomes and output, which affect the status of the interface. Chapter 6 discusses the interplay between front-end and business-logic modeling.
- Implementation may exploit model transformations and code generation to produce prototypes of the user interface or even fully functional code. In chapter 10 we discuss how to implement IFML models manually in some representative software platforms, and then in chapter 11 we exemplify the automation of the development activities achieved with model-driven tools.
- Testing and evaluation can be anticipated and performed on the IFML models rather than on the final code. Model checking may discover inconsistencies in the design of the front end (e.g., unreachable statuses of the interface) and suggest ways to refactor the user interface for better usability (e.g., recommend uniform design patterns for the different types of user interactions, such as searching, browsing, creating. modifying, and deleting objects).
- Finally, maintenance and evolution benefit most from the existence of a conceptual model of the application. Requests for changes are analyzed and turned into changes at the design level. Then, changes at the conceptual level are propagated to the implementation, possibly with the help of model-to-code transformation rules. This approach smoothly incorporates change management into the mainstream production lifecycle and greatly reduces the risk of breaking the software engineering process due to the application of changes solely at the implementation level.

### A Complete Example

As a conclusion to this brief introduction of IFML, we present a simple, yet complete, example. The application is an online store where the user can browse products, such as books, music, and software, and add products to his shopping cart, as shown by the UML use case diagram of Figure 2.10.

The application has a web front end. In the “Browse books” use case, the user accesses a home page that contains a list of product categories. Clicking on a product category such as “Books” leads to a page displaying the summary data about all the items of that category. Clicking on a “See more” associated with one item’s summary opens a page where the full details of the selected object are presented. Figure 2.11 shows the mock-ups of the application front end supporting the “Browse books” use case.

When looking at the details of an item, the user can press the “Add to cart” button to add the item to his virtual shopping cart. A modal window appears where the user can specify the quantity of goods he wants to purchase. After submitting the desired quantity, a confirmation pop-up window is presented to acknowledge the addition of the product to the cart. Figure 2.12 shows the mock-ups of the interface supporting the “Manage cart” use case.

The IFML model of the Bookstore application contains the five ViewContainers shown in Figure 2.13.

The ViewContainers are annotated with stereotypes (such as H, for “Home,” L for “Landmark,” and “Modal” and “Modeless”) that further specify their properties. These are discussed in chapter 4.

The ViewContainers definition is refined by specifying the ViewComponents they comprise, as illustrated in Figure 2.14.

Interactivity is represented by adding the relevant events and specifying the interaction flows they trigger, along with the parameter binding between the source and the target components of the interaction flows. The model of Figure 2.15 shows that the “CategoryList” ViewComponent supports an interactive event “SelectCategory,” whereby the user can choose a category from the index. As a result, the “ProductOfCategory” page is displayed, and the “ProductList” ViewComponent shows the items corresponding to the chosen category. The input–output dependency between the “CategoryList” and the “ProductList” ViewComponents is represented by the parameter binding group, which associates the “SelectedCategory” output parameter of the source component with the “Category” input parameter of the target component. The same modeling pattern is used to express the interaction for selecting a product from the “ProductList” component and then accessing its data in the “ProductDetails” component.

Some event may trigger the execution of a piece of business logic. As an example, Figure 2.12 and Figure 2.16 show the activation of an action for inserting items in the shopping cart. After the user presses the “Add to cart” button associated with the “ProductDetails” component, a modal window appears asking for the quantity of items desired. The quantity submission event triggers the execution of the “Add to cart” action. The “Quantity” value from the Form ViewComponent and the “DisplayedProduct” parameter from the “ProductDetails” ViewComponent are submitted as input parameters to the “Add to cart” action. Once the action is completed, a confirmation window is displayed.

Notice that the binding of the “Quantity” output parameter is associated with an interaction flow, which denotes the effect of a submit event that requires the user’s interaction. Conversely, the binding of the “DisplayedProduct” parameter is associated with a data flow, which merely expresses an input–output dependency automatically performed by the system and not triggered by a user’s interaction.

## Modeling the composition of the user interface

### Interface Organization

The specification of the interface in IFML is organized hierarchically using modularization constructs called ViewContainers.

#### ViewContainers
A ViewContainer is an element of the interface that aggregates other view containers and/or view components displaying content.
In practice, a ViewContainer may represent a physical interface artifact such as a window or a page of a web application. But it can also denote a purely logical aggregation of other view containers, such as a section of a large web portal constituted by several pages dealing with a homogeneous subject.
ViewContainers support navigation, which is the change of focus from one container to another. To specify that a ViewContainer is the source of a navigation command, it is necessary to associate it with an event.

#### Events
An Event is an occurrence that can affect the state of the application by causing navigation and/or passing parameters. Events may be produced by a user interaction (ViewElementEvent), by an action when it finishes its execution normally or exceptionally (ActionEvent), or by the system in the form of notifications (SystemEvent).
A ViewElementEvent is an Event that may be triggered by the user while interacting with ViewContainers, ViewComponents, and parts thereof called ViewComponentParts.
The effect of user interaction—that is, the target ViewContainer displayed after a ViewElementEvent has occurred—is specified by means of a NavigationFlow, denoted as a directed arc connecting the event symbol to the target view container.

#### NavigationFlow
A NavigationFlow represents the navigation or the change of the view element in focus, the triggering of an Action, or the reaction to a SystemEvent. NavigationFlows are activated when Events are triggered. They connect Events owned by ViewContainers, ViewComponents, ViewComponentParts, or Actions with other ViewContainers, ViewComponents, ViewComponentParts, or Actions.
Figure 4.1 shows a very simple IFML model exemplifying these concepts, together with a hypothetical rendition.
“Source” and “Target” are ViewContainers, denoted as UML classifiers. “ClickMe” is an Event, represented as a circle associated with the owning ViewContainer. The NavigationFlow, denoted by an unlabeled directed arrow, connects the event named “ClickMe” of the “Source” ViewContainer to the “Target” ViewContainer, indicating that the occurrence of the “ClickMe” event causes the display of the “Target” ViewContainer.
Notice that some model features, such as the name of the ViewContainers and of the Event, are purposely shown also in the rendition. This is to highlight that the model features can be employed to create the implementation. For example, the name of the ViewContainer could be used to produce the title of a window or the name and URL of a web page, and the name of an Event could be exploited to create the text of a hyperlink anchor or a button label.

### View Container Nesting

Most interfaces organize the content and interaction commands presented to the user into a regular structure to enhance usability. For example, many web pages have a central content area and one or two columns for collateral items such as menus, search bars, and ads. Window-based interfaces split the work area into several panels and use tabbing to present alternative views of the work items.
IFML models the structure of the interface by means of nested ViewContainers. Nested ViewContainers express the organization of the interface at a conceptual level but necessarily have an interpretation that depends on the platform where the interface is deployed. Two typical situations arise:
- In window-based platforms, such as Java Swing or Windows.NET, the interface is normally hosted within one top-level container.
- In a pure HTML web application, the interface is normally fragmented across a set of independent page templates, which means that there is no top-level ViewContainer. Rather, one ViewContainer is elected as the one accessed by default (the so-called “Home Page”).
The advent of rich Internet applications has blurred the distinction between window-based and page-based interfaces, so it is not uncommon to see interfaces that have an organization that stands in the middle between the two extremes. This is in line with the single page development paradigm.
In the rest of this section, we proceed in the explanation of the features of ViewContainers from a platform-independent perspective. We will come back to the influence of platform-dependent features on design when discussing interface design patterns later in this chapter. In chapter 7, we will present some extensions to IFML conceived for desktop, web, and mobile development, which customize the terminology and concepts of IFML to make the language closer to the expectations of developers of these popular classes of solutions.
Nested ViewContainers may be in conjunctive form, which means that they are displayed together, or in disjunctive form, which means that the display of one ViewContainer replaces another ViewContainer. The property of disjunctiveness is explicitly associated with the enclosing container with the notation shown in Figure 4.2: a XOR label before the name of the ViewContainer. By default, ViewContainers display their inner ViewContainers in conjunctive form.
Figure 4.3 shows an example of disjunctive ViewContainers from the e-mail application used as a running example. The interface consists of a top-level ViewContainer from which the user can access either the “MailMessages” ViewContainer or the “Contacts” ViewContainer.

### View Container Navigation

ViewContainers support a basic form of navigation, which we call content-independent navigation to mark the distinction with the content-dependent navigation described in chapter 5.
Content-independent navigation is expressed by associating a navigation event to a ViewContainer and by specifying the target of the navigation with an InteractionFlow. An example of this design pattern was illustrated in Figure 4.1.
The meaning of content-independence is that user interaction does not depend on the content of the source and destination ViewContainers. In implementation terms, it is not necessary to associate parameter values with the interaction in order to compute the content of the target ViewContainer. This behavior is in contrast to content-dependent navigation, discussed in chapter 5.

### View Container Relevance and Visibility

ViewContainers are characterized by some distinguishing properties that highlight their “importance” in the organization of the interface.

#### Default ViewContainers
The default property characterizes the ViewContainer presented by default when its enclosing ViewContainer is accessed.
Default view containers are denoted by a “D” within square brackets placed at the top-left corner of the view container.

#### Landmark ViewContainers
The landmark property characterizes a ViewContainer that is reachable from all the other ViewContainers nested within its enclosing ViewContainer (i.e., from its sibling ViewContainers) and from their subcontainers.
Landmark view containers are denoted by an “L” within square brackets placed at the top-left corner of the view container.
Figure 4.4 shows an example of the landmark and default properties in the e-mail application. When the user starts the application the “Mail” ViewContainer is accessed. The default subcontainer “MailMessages” is displayed, whereas the alternative ViewContainer “Contacts” remains hidden. Both “MailMessages” and “Contacts” are defined as landmarks, which means it is always possible to access the one that is not in view from the one that is in view.
The landmark property is an example of a construct introduced for model usability. It does not augment the expressive power of IFML, because the access to ViewContainers can be represented explicitly with navigation flows, but reduces the burden of model specification and augments the readability of diagrams. Figure 4.5 illustrates on a small scale example why this is true. It shows two equivalent IFML diagrams. In the diagram on the left, the ViewContainers nested inside the Top ViewContainer are marked as landmarks, which means that every ViewContainer is the target of an implicit navigation flow pointing to it from the sibling ViewContainers. The diagram on the right explicitly shows these navigation flows and the events triggering the navigation. The meaning conveyed by the diagram on the left is that a landmark ViewContainer can be reached from any other ViewContainer of the enclosing module. If an interface contains many containers, the landmark property significantly reduces the number of events and navigation flows to be drawn and makes the diagram much more readable.
Figure 4.6 shows an example with nested ViewContainers. ViewContainer “One” is landmark and thus accessible from its sibling ViewContainers and their children (i.e., from the ViewContainers “Two,” “Three,” and “Four”). The same applies to ViewContainer “Two.” Again, the use of the landmark property avoids cluttering the diagram with many events and navigation flows.

### Windows

IFML provides a set of specializations of the ViewContainer concept that allow one to represent more precisely the behavior of the container-level navigation.

#### Window
A Window is a specific kind of ViewContainer that represents a window in a user interface. A Window ViewContainer can be tagged as Modal or Modeless depending on its behavior with respect to the user interaction. A Modal window opens as a new window and disables the interaction with the background window(s) of the application; a Modeless window opens as a new window and still allows interaction with the other pieces of the user interface.
Navigation from a source window to a target window (not tagged as Modal or Modeless) implies that the source window disappears and is replaced by the target. If the target Window is tagged as Modal or Modeless instead, the new window will be superimposed onto the old one and will behave as modal or modeless respectively. Window, Modal, and Modeless specializations can be specified as stereotypes of the ViewContainer classifier, as shown in Figure 4.7.
Navigation between Windows “Step 1” and “Step 2” implies that “Step 2” substitute “Step 1” on the screen. Navigations from “Submission” to “Confirmation” and “ToolsMenu” will open the two new windows in front of the old one and will respectively grant modal and modeless behavior.

### Context and Viewpoint

The composition of the interface is not necessarily a static concept. Many applications update the interface organization and content at runtime, based on information about the context of the user interaction. For example, a mobile application can deliver alerts based on the current position of the user, and a web-based portal may exploit the information of the personalization subschema, introduced in chapter 3, for publishing user profile data and personalized recommendations.
To support the dynamic adaptation of the interface, IFML comprises concepts that capture both the design-time adaptation requirements set by the developer and the runtime values set by the application, which are necessary for deciding which adaptations to apply based on the interaction context of the user. The notion of context provided by IFML is purposely very broad. It may encompass aspects such as the identity, role, geographic position, or device of the user.

#### Context and ContextDimension
The Context is a descriptor of the runtime aspects of the system that determine how the user interface is adapted. A ContextDimension is a component of the Context.
IFML comes with various predefined extensions of the ContextDimension concept.

#### UserRole, Device, and Position
The UserRole represents the role currently played by the user in the application. It comprises the attributes that the user’s profile should satisfy to enable the context.
Device represents the characteristics that a device possesses.
Position represents the availability of location and orientation information of the device used to access the application.
The predefined Context and ContextDimension elements can be extended to represent finer-grain or other context perspectives, such as network connectivity or temporal aspects.
The requirements for a Context to be active are expressed by OCL expressions, called ActivationExpressions.

#### ActivationExpression
An ActivationExpression is a Boolean condition that determines whether the associated Context (or other IFML element) is active (if the condition is true) or inactive (if the condition is false).
Figure 4.8 shows the IFML notation for an ActivationExpression that specifies when a Context is active. The specific context is represented as an instance (“AdminMobileContext”) of a classifier stereotyped as «context». The ActivationExpression is expressed as a stereotyped annotation associated to the Context instance.
The example of Figure 4.8 assumes that the “UserRole” ContextDimension has an attribute called “RoleName” that specifies the role that the user should fulfill in a role-based access control (RBAC) system. It also assumes that the “Device” ContextDimension has two attributes. “Type” identifies the class of device, while “Size” indicates the dimensions of the screen. The specification of Figure 4.8 therefore mandates that the “CustomerMobileContext” is enabled when the user’s access device is a small screen tablet and the role granted after login is that of a registered customer.
The evaluation of an ActivationExpression associated with a context requires that the values of the relevant ContextDimensions be recorded at runtime. Such runtime values can be represented in IFML as ContextVariables.

#### ContextVariable
A ContextVariable is a runtime variable that holds information about the usage context. It specializes into SimpleContextVariable (of a primitive value type) and DataContextVariable (referencing a DataBinding).
ContextVariables enable a form of fine-grain interface adaption, as we will see in chapters 7, 8, and 9. They can be used in ActivationExpressions associated with ViewElements to condition their visibility based on the situation. Another, coarser-grain form of interface adaptation is achieved by using ViewPoints, which denote whole application designs tailored for a specific context.

#### Viewpoint
A ViewPoint is the specification of an entire interface model that is active only when a specific Context is enabled.
The enablement of the ViewPoint is dynamic and governed by the ActivationExpression associated with the Context. When the ActivationExpression is satisfied, the Context becomes active and so does the associated ViewPoint with all the ViewElements and Events contained in it.
Figure 4.9 shows an example of ViewPoint specification. Two ViewPoints are defined (“Admin” and “Editor”) that contain different interface models for the two distinct roles. They are associated with the contexts that specify the activation requirements of the ViewPoints.
In summary, the ContextDimensions express the enabling dimensions of the Context, and an ActivationExpression can be used to dictate the required values for such ContextDimensions. The actual runtime values for a specific user are represented by ContextVariables. When the relevant runtime values of the ContextVariables match the required values for the ContextDimensions in the ActivationExpression, the Context is enabled. The enabled Context in turn identifies the ViewPoint (i.e., the variant of the interface) to be used. Finer-grain adaptation can be achieved using ContextVariables in ActivationExpressions associated with individual element of the interface.
The values of the ContextVariables can also be used to publish or to put to work the content of the personalization schema
- A ContextVariable holding the user’s identity (e.g., the “username” attribute) permits the application to look up the appropriate instance of the “User” class of the personalization subschema, retrieve profile data and personal objects from the database, and publish them in the interface.
- A ContextVariable holding the role of an authenticated user can be used to look up the appropriate instance of the “Group” class in the personalization subschema, retrieve the permissions of the user, and adapt the interface content and actions to such permissions.
In chapter 7, we put these concepts to work in various examples of the adaptation of the interface for web and mobile applications. In chapter 8, we discuss how to set the ContextVariables explicitly based on user interaction (e.g., as the effect of a login Action) and how to use them in applications exploiting the identity and role of the user.

### User Interaction Patterns

The proper organization of the interface is paramount for getting a good and user-friendly experience. IFML allows the designer to express such an organization at a conceptual level before committing to the implementation architecture. To support the design of the interface structure, we introduce a set of guidelines based on user interaction patterns, reusable models that effectively address a recurrent set of requirements in the design of user interfaces. When most users become accustomed to a successful pattern, new applications tend to implement the same design to reduce the learning curve and induce a sense of familiarity. User interaction patterns are classified into various categories, based on the concern addressed.
We will use a pattern naming convention to help designers immediately identify the purpose of a pattern. The name of a pattern is structured as XY-Z, where:
- X is the category of pattern. For instance, interface organization patterns start with the letter “O.”
- D is the deployment platform. For instance, desktop patterns are labeled with “D,” web with “W,” and mobile with “M.” The letter “G” (for “general”) is reserved for cross-platform patterns that apply irrespective of the deployment platform.
- Z is a mnemonic label identifying the specific pattern.
For instance, a pattern could be named OD-SWA (as in the first example described in section 4.8.1.1).

### Interface Organization Patterns and Practices

An interface organization pattern is a user interaction pattern that focuses on the hierarchical structure of the user interface. Different interface organization patterns have emerged for different classes of applications and for the various delivery platforms and access devices. This section reports some of the best-known patterns in this category, classified by platform (desktop, web, and mobile). Other categories of patterns are presented in the next chapters.

#### Desktop Interface Organization Patterns

In desktop applications—and more recently in single-page rich Internet applications—the entire user interface is hosted within a single topmost ViewContainer, which has an articulated internal structure based on a hierarchy of nested ViewContainers.

##### PATTERN OD-SWA: Simple work area

A typical functional division distinguishes a work area where the main tasks of the application are performed from one or more service areas, including ViewContainers either hosting commands (e.g., menu bars, tool bars) or supporting auxiliary tasks (e.g., console or error message panels, status bars).
Figure 4.10 shows the IFML model of the simple work area interface organization pattern with an example application (a text editor). The pattern simply comprises a top-level ViewContainer with embedded nested sub-ViewContainers.

##### PATTERN OD-MWA: Multiview work area

When the task supported by the application and the data or the objects to be manipulated grow in complexity, the simple work area organization can be refined. One extension is to allow for multiple alternative views of the object/data/task in the work area, as represented by View1 and View2 in Figure 4.11.
Figure 4.11 shows an example of the multiview work area interface organization. An image editor has a normal view shown by default (called “Home”) and a zoom view used for adjusting the zoom level of the image (called “View”).

##### PATTERN OD-CWA: Composite work area

An alternative way of breaking down complexity is to split the work area into subregions devoted to different subtasks or perspectives of the object/data/task, presented simultaneously to allow the user to switch without losing the focus on the item under consideration. In such a case, one subregion often hosts the principal representation of the object/data/task and the other regions support collateral properties or subtasks.
Figure 4.12 shows an example of a composite work area interface with an example application: a document editor, featuring the main work area with a set of associated panels plus a set of menu bars.

##### PATTERN OD-MCWA: Multiview composite work area

The decomposition of the work area into alternative perspectives and simultaneous partial views can be combined to achieve a nested structure that best fits the specific requirements of the task supported by the application. For example, the work area could be partitioned into partial views displayed simultaneously, and the main view could be organized into multiple perspectives. Another option could have the work area supporting alternative perspectives, each one composed of several partial views appropriate to a perspective, displayed simultaneously.
Figure 4.13 shows an example of a multiview composite work area: a programming language IDE has an editing and a debug view, the latter composed of several parts.

#### Web Interface Organization Patterns

In web applications, the typical organization of the interface allocates functionality to multiple pages, either produced statically or generated dynamically by page templates or server side scripts. In this case, nested ViewContainers are still useful and can fulfill a twofold role. As with desktop applications, they may express the allocation of content and navigation within regions of a page (e.g., as is possible with HTML frames or through the use of JavaScript). In contrast to desktop applications, they may express the logical clustering of multiple pages that have some common characteristics, for the purpose of modularizing the web application and supporting cross-site navigation mechanisms.

##### PATTERN OW-MFE: Multiple front-ends on the same domain model

In many cases, the web is used as a technical architecture to deliver a set of applications on top of the same data, represented in the domain model. A classical case is that of content management systems (CMS). These applications support two roles, as shown in Figure 4.14: the content editor and the reader, which have different use cases and must be served by distinct front ends acting upon the same data. In such a scenario, the pages constituting the two applications could be clustered into two distinct top-level containers, one for the editor and one for the reader.
Such an organization brings several benefits:
- It expresses a functional modularization of the front end that could be exploited, for example, to partition the implementation effort across different teams.
- It allows ViewContainers to be used as resources in a role-based access control policy. Users with role “editor” will access the pages of the “Editor” ViewContainer, whereas users with role “reader” will access the pages of the “Reader” ViewContainer.
- It enables a better management of the implementation artifacts, including the deployment at different web addresses and the separation of graphic resource files.
Figure 4.15 shows an example of multiple front ends interface composition pattern applied to a content management application serving the roles and use cases illustrated in Figure 4.14. A top-level ViewContainer “Login” denotes a public page for logging into the application, common to both roles. Then two nested ViewContainers comprise the ViewContainers that denote the web pages specific to the use cases of each role.
The dynamic activation of the appropriate interface after a user request based on his role can be specified using the Context and Viewpoints introduced in chapter 3. For each role, a Context with the appropriate ActivationExpression on the “UserRole” ContextDimension can be defined and associated with a ViewPoint that comprises the ViewContainers of Figure 4.15 appropriate for that role.

##### PATTERN OW-LWSA: Large web sites organized into areas

ViewContainers also come handy for expressing the logical organization of many real-world web applications that exhibit a hierarchical structure whereby the pages of the site are clustered into sections dealing with a homogeneous subject. Nested ViewContainers can play the role of “site areas,” recursively structured into other subareas and/or pages. Most real-life web sites exhibit an organization into areas. For example, Figure 4.16 shows an interface fragment taken from a web site whose pages include a navigation bar with anchors pointing to the various areas of the site.
In chapter 7, we will exploit the native extension mechanism of IFML to introduce specializations of the ViewContainer concept that make the specification of web interface organization patterns more expressive.

#### Mobile Interface Organization Patterns

Mobile interface organization must account for the reduced screen space of portable devices and for the usage context, whereby users often access the application in unconformable conditions, such as while standing or walking. Therefore, a consistent usage of the scarce screen space is the number one rule of interface organization to reduce the learning curve and minimize the interactions needed to perform tasks. This requirement constrains the top-level organization, which repeats consistently across mobile operating systems and individual applications.
In this section, we introduce only one high-level interface organization pattern. We defer to chapters 7 and 8 the illustration of several other design patters for mobile applications based on the interplay between the organization of the main interface containers and the content components.

##### PATTERN OM-MSL: Mobile screen layout

The basic organization of the interface of mobile applications maps the interface to a top-level grid that contains three regions: the header, the content area, and the footer, as shown in Figure 4.17.
The header is normally used for command menus and notifications. Part of the header may be reserved for operating-system notifications and therefore remains fixed across all applications. The content area normally has a simple layout that limits the use of multiple perspectives and nested panes to a minimum and exploits scrolling along one dimension to accommodate content that overflows the size of the screen. The footer region is normally allocated to system-level commands, such as general or application-specific settings menus.
This essential design pattern can be articulated in a variety of more specific forms depending on the device capacity, the content type, and the application requirements. Chapters 7 and 8 provide many examples of IFML extensions that make the models of mobile applications more expressive and introduce several design patterns that recur in different classes of mobile applications.

### Running Example

We return to the running example of the e-mail management application started in chapter 3 to show how to model the organization of the interface.
When the user accesses the application, the interface presents by default the functionality for accessing mailboxes and managing messages, as shown in Figure 4.18.
An equivalent interface is available for contact management, which is accessed upon request. Its organization is shown in Figure 4.19.
The application lets the user always switch from one view to the other by means of a menu, as shown in Figure 4.20.
The message management interface comprises an area for working with mailboxes and messages. This area is displayed by default, as shown in Figure 4.18. If the user activates the compose command, the mailbox and message area is replaced with a message composer interface, shown in Figure 4.21. Similarly, if the user activates the “Settings” command, a pop-up panel for editing options and preferences is displayed, as shown in Figure 4.22.
The area for working with mailboxes and messages displays a search panel, a toolbar, and a mailbox/message display region, as visible in Figure 4.18. When a message is selected, the message list is replaced with the visualization of the message content, as shown in Figure 4.23.
The message search box alternates between two interfaces for searching: a simple keyword input field, visible in Figure 4.18, and an advanced search form with multiple fields, shown in Figure 4.24.
Figure 4.25 shows an excerpt of the IFML model that specifies the organization of the interface of the e-mail application sketched in Figures 4.18–4.24. The top ViewContainer (“Mail”) hosts two alternative subcontainers: one for message management and one for contact management. For brevity, we illustrate only the internal structure of the default ViewContainer (“Messages”). Its structure comprises two ViewContainers that are displayed together: “MessageSearch” and “MessageManagement.”
The “MessageSearch” ViewContainer comprises two mutually exclusive landmark subcontainers: “Search” (shown by default) and “FullSearch.” The “MessageManagement” ViewContainer comprises three mutually exclusive landmark subcontainers: “MailBox” (the default), “Settings,” and “MessageWriter.” The “MailBox” ViewContainer consists of the “Message Toolbar” and the “MessageViewer” containers displayed simultaneously. Finally, the “MessageViewer” ViewContainer comprises the “MessageList” and the “MessageDetails” subcontainers, which are visualized in alternative.

## Modeling interface content and navigation

ViewElements are distinguished in ViewContainers (already treated in chapter 4) and ViewComponents, which are the main subject of this chapter.
Events and InteractionFlows have been already introduced in chapter 4 but acquire a more interesting meaning in content and navigation modeling. They enable the specification content-dependent navigation, that is, a form of interaction that exploits the objects of the domain model. The simplest example of content-dependent navigation is the selection of items from a list. The user accesses a ViewComponent that displays a list of objects, selects one, and accesses another ViewComponent that displays detailed information about the chosen object.
On the one hand, content-dependent navigation is similar to content-independent navigation, described in chapter 4:

- It involves a source and a destination element and is expressed by means of an Event and of a NavigationFlow.

- On the other hand, it has important differences: typically the source and target of the navigation are ViewComponents (and not ViewContainers). Furthermore, the target ViewComponent normally depends on some data provided by the source ViewComponent; this dependency is expressed by associating one or more ParameterBinding specifications to the NavigationFlow.

The specification of ViewComponents can be done at different levels of precision:

- At the most abstract level, a ViewComponent is just a “box with a name,” as in the preliminary examples introduced in chapter 2 (e.g., see Figure 2.2). Its meaning is conveyed only by the name, without further details except for the optional specification of subcomponents specified with the IFML ViewComponentPart construct. Using this level of abstraction keeps the specification very general and easy to produce but may overlook important information needed for model checking and code generation.
- At an intermediate level of abstraction, IFML allows a standard way of binding ViewComponents to elements of the domain model. This is extremely useful to express, for example, that a ViewComponent “Index of Products” actually derives its content from the instances of a “Product” class of the domain model. This additional knowledge can be used for checking the consistency between the IFML model and the domain model and for automatically generating the data query that extracts the content of the “Index of Products” ViewComponent.
- At the most refined level, the ViewComponent construct can be extended with specialized subclasses to express specific ways in which content is presented or exploited to enable user interaction. For example, a List ViewComponent can be defined to represent a specific ViewComponent aimed at publishing an ordered set of objects from which the user can select one item. Extended components may have domain-dependent properties and thus enable deep model checking and full code generation.

In this chapter we discuss both the basic IFML notion of ViewComponent and the extensions already defined in the standard. In chapter 7 we illustrate how the designer can introduce novel extensions, using web and mobile application development as examples.

### What ViewContainers Contain: ViewComponents

A ViewContainer may comprise ViewComponents.

**ViewComponent**

A ViewComponent is any element that can display content in the user interface or accept input from the user.

Examples of ViewComponents are interface elements for visualizing the data of one object, for displaying a list of objects, data entry forms for accepting user input, and grid controls for displaying and editing data tables. A ViewComponent may have an internal structure consisting of one or more ViewComponentParts.

**ViewComponentPart**

A ViewComponentPart is an interface element or a structural property that may not live outside the context of ViewComponent.

The meanings of ViewComponent and of ViewComponentPart are left purposely broad. Their semantics are defined by the designer and conveyed by the component/part name. Figure 5.1 shows the graphic representation of ViewComponents and some exemplary renderings. As can be noted, at the highest level of abstraction only the name of the component is used to suggest the intended meaning.

### Events and Navigation Flows with ViewComponents

ViewComponents and ViewComponentParts can support interaction. This capacity is denoted by associating them with Events, which in turn enable NavigationFlows. Figure 5.2 shows an example of an interactive ViewComponent. The “ProductList” ViewComponent is associated with an Event “SelectProduct,” which is the source of a NavigationFlow leading to the “ProductDetails” ViewComponent. The meaning of this design pattern is that “ProductList” publishes a list of objects from which the user can select. The selection event triggers an interaction, whose effect is showing the information of the chosen object in the “ProductDetails” ViewComponent.
In content-based navigation, the source and destination ViewComponents can be positioned in different ViewContainers, as shown in Figure 5.2. In this case, the navigation event has the effect of showing the target ViewContainer and of triggering the computation of the ViewComponents present in it. The display of the target ViewContainer may impact the visualization of the source ViewContainer in one of two ways:
- If the source and target ViewContainers are mutually exclusive (either directly or because they are nested within mutually exclusive ViewContainers), the target replaces the source.

- Otherwise the target is displayed in addition to the source.

For example, Figure 5.3 shows the ViewComponents, Event, and NavigationFlow of Figure 5.2, but this time both the source and target ViewComponent are in the same ViewContainer. This indicates that the choice of one product in the list causes the display of the details in the same ViewContainer.

### Content Dependencies: Data Binding

ViewComponents publish content in the interface. It is therefore necessary to specify the source of the published content. This aspect is represented by means of the ContentBinding specification.

**ContentBinding**

A ContentBinding is a very general representation of the content source of a ViewComponent; its only attribute is the URI of the resource from which the content may be obtained.

Figure 5.4 shows a simple example of ContentBinding: the “FeedReader” ViewComponent is associated with a ContentBinding specification that references the URL of the feed provider.
To represent the common situation in which the content published by a ViewComponent originates from the objects of the domain model or from an external service, the ContentBinding concept is refined in two specializations: DataBinding and DynamicBehavior.

**DataBinding**

A DataBinding represents the provenance of content from objects of the domain model; it is characterized by features that specify the type of data, the criterion for selecting instances, and the attributes relevant for publication.

More precisely, a DataBinding is associated with:

- a reference to a domain model concept (depending on the type of domain model, the referenced concept can be a UML classifier—which may represent a class in the domain model, an XML file, a table in a database, etc.—or another element);

- a ConditionalExpression, which determines the specific instances to be extracted from the content source;
- one or more VisualizationAttributes, used by the ViewComponent to locate the data shown in the interface, such as an object attribute, a database column or an XML element or attribute; and

- an optional OrderBy ViewComponentPart, which lists one or more sorting criteria consisting of an attribute name and a sort direction (ASC or DESC for ascending or descending, respectively).

Figure 5.5 shows an example of a simple DataBinding. The “MessageList” ViewComponent draws its content from the “MailMessage” entity of the domain model. The DataBinding neither specifies which instances are to be published nor the attributes to be visualized, and so these aspects are left unspecified.
Figure 5.6 refines the example of Figure 5.5. The DataBinding contains an OCL ConditionalExpression “self.isRead = false,” which specifies that only the instances of the entity “MailMessage” with the attribute “isRead” equal to false should be published. The VisualizationAttributes ViewComponentPart specifies that the attributes “subject” and “date” should be used to display the objects, and the OrderBy ViewComponentPart indicates that they are sorted in descending order of date.
Note that because the conditional expression is defined within the DataBinding ViewComponentPart, the context of the expression is implicitly set to “MailMessage” (i.e., the object referenced by the DataBinding).

The DataBinding represents the association of a ViewComponent to the content elements in a declarative way, which facilitates the generation of the data extraction queries. An alternative way of expressing the content of a ViewComponent is through the DynamicBehavior element.

**DynamicBehavior**

A DynamicBehavior represents the data access of a ViewComponent in an operational way (e.g., through the invocation of a service or method that returns content).

For instance, a DynamicBehavior can be expressed by referencing any UMLBehavior or UMLBehavioralFeature.

Figure 5.7 shows an example of DynamicBehavior used to specify that the “TweetList” ViewComponent exploits the web API of an external service to publish content.

### Input-Output Dependencies: Parameter Binding

Content-dependent navigation allows expressing the very common situation in which one component displays content that depends on some previous interaction performed by the user. Examples are the display of the data of an object previously selected from a list, the display of the result list of a keyword search, and the drill-down into a hierarchy.

All these situations require expressing an input–output dependency between ViewComponents. The ViewComponent target of the navigation requires input provided by the source ViewComponent for retrieving the content to publish. An input–output dependency is described by means of the ParameterBinding construct.

**ParameterBinding and ParameterBindingGroup**

A ParameterBinding specifies that the value of one parameter, typically the output of some ViewComponent, is associated with that of another parameter, typically the input of another ViewComponent. When the input–output dependency involves several parameters at the same time, ParameterBinding elements are grouped into a ParameterBindingGroup.

Figure 5.8 shows an example of an input–output dependency. The “MessageList” ViewComponent displays the messages of the specific mailbox selected by the user in the “MBoxList” ViewComponent. The NavigationFlow is associated with a ParameterBindingGroup that contains the declaration of an input–output dependency: the value of the parameter “SelectedMailBox” (output of the “MBoxList” ViewComponent) is associated with the value of the parameter “MailBox” (input of the “MessageList” ViewComponent). The value of the “MailBox” parameter is used in the ConditionalExpression of the “MessageList” ViewComponent, specified by the following OCL expression:
```ocl
self.MailMessageGroup = MailBox
```
The OCL expression specifies that the instances of “MailMessage” to retrieve are those associated by the relationship role “MailMessageGroup” with the object identified by the value of the parameter “MailBox.” The pattern of Figure 5.8 provides an example of a ConditionalExpression that exploits an association in the domain model.
The transfer of parameters necessary for satisfying the input–output dependencies between correlated components does not always requires user intervention.
Figure 5.9 shows an example of such a situation. When one contact is selected in the “ContactList” ViewComponent, the details of the selected object are displayed in the “ContactInfo” ViewComponent. In addition, further information about the same object is displayed, namely, the list of addresses and e-mails in the “Addresses” and “Emails” ViewComponents respectively. These two components are displayed simultaneously with the “ContactInfo” ViewComponent after the selection from the list without any further user interaction. The input parameter needed for computing their content (the ID of the selected contact) is provided by a ParameterBinding associated with the DataFlows from the “ContactInfo” ViewComponent to the “Addresses” and “Emails” ViewComponents.

**DataFlow**

A DataFlow is an InteractionFlow that specifies that some parameters are supplied from a source to a target element, without any user’s interaction; the involved parameters are specified by means of a ParameterBindingGroup associated with the DataFlow.

DataFlows emanate directly from ViewComponents rather than from Events and are denoted with dashed arrows to distinguish them from NavigationFlows.

### Extending IFML with Specialized ViewComponents and Events

The examples of the previous sections introduced a rather rudimentary notion of ViewComponent. So far this concept is little more than a box. Its meaning is conveyed only by the name assigned to it by the designer. In this way, however, the model usability and semantics cannot be improved much. If “all boxes are equal,” tools could not check the correctness of the models or support the designer with useful inferences and shortcuts.
To allow deeper model checking and improve model usability, IFML supports the extension of the basic ViewComponents with user-defined specializations. Figure 5.10 illustrates the extensions of the base ViewComponent construct already provided in the IFML standard, which are still quite general. More extensions will be introduced in chapter 7 for web and mobile applications.
The List and Details ViewComponents just add a stereotype to the basic ViewComponent concept. The Form ViewComponent also adds novel ViewComponentParts (SimpleField and SelectionField).

#### Data Publishing Extensions

IFML component extensions are represented in the model by stereotypes added to a ViewComponent. For the sake of conformance to the IFML standard, we use textual stereotyping, which is quite cumbersome for ViewComponents, especially when their names are long. However, a tool may replace the textual notation of stereotypes with a more concise representation to save screen space (e.g., small icons, font colors, textures).

**List ViewComponent**

A List ViewComponent is a ViewComponent used to display a list of objects retrieved through a ContentBinding. When the List ViewComponent is associated with an Event, it means that each object displayed by the component can be used to trigger the Event. Firing the Event causes the passing of the chosen instances as a parameter value to a target IFML element.

**Details ViewComponent**

A Details ViewComponent is a ViewComponent used to display the attribute values of one object retrieved through a ContentBinding. When the Details ViewComponent is associated with an Event, it means that the instance displayed by the component can be used to trigger the Event. Firing the Event causes the passing of the displayed instance as a parameter value to a target IFML element.

Figure 5.11 shows an example of List and Details ViewComponents connected with an event and a navigation flow. The “MessageList” publishes the list of all “MailMessage” instances. The “select” event indicates that the “MessageList” ViewComponent supports interaction (i.e., the user can click on one of the displayed object and trigger the event). The firing of the event produces the display of the “Message” Details ViewComponent, which receives as input the chosen “MailMessage” object.
The selection from a list is an event frequently associated with ViewComponents. It thus has a specific representation in IFML as an extension of the base Event concept, shown in Figure 5.11 (and previously in Figures 5.2, 5.3, 5.8, 5.9).

**SelectEvent**

A SelectEvent is a kind of Event that supports the selection of one or more elements from a set. When triggered, it causes the selected value(s) to be passed as a Parameter to the target of its associated NavigationFlow.

In chapter 6 we will introduce another refinement of the Event, the “select all” event, which is used to express an Event that supports the selection of all elements of a set.
Figure 5.12 shows an example that illustrates how adding more semantics to the model via IFML extensions can improve usability. The model representation is more concise than that of Figure 5.11, but the usage of extensions with precise semantics easily allows a tool (or a human reader) to infer that the two models are equivalent. Indeed, the List ViewComponent publishes a set of instances of the “MailMessage” class, the Details ViewComponent publishes one instance of the same class, and the “select” Event actually allows the user to select one item from the source ViewComponent and pass it to the target ViewComponent. Thus the designer could draw the more concise variant of Figure 5.12, sparing the effort of expressing the inferable ParameterBinding and ConditionalExpression.
The selection from a list can also include multiple items, as supported by the multichoice list ViewComponent.

**MultiChoiceList**

The MultiChoice List enables the selection and submission of multiple instances. It supports multiple event types. The standard select event expresses the selection of one element of the list, while the checking and unchecking events express the application or removal of a selection ticker on any element in the list. The set selection event denotes the submission of the entire set of objects, and the submit event denotes the submission of the currently selected objects.

An example of a multichoice list is shown in Figure 5.31 and in the multiple-object deletion pattern discussed in chapter 8.

#### Data Entry Extensions

Besides content publishing, IFML extensions can also be used to express data entry. This is done using the Form ViewComponent extension.

**Form**

A Form is a ViewComponent that represents a data entry form.

A form comprises one or more ViewComponentParts that represent input fields (and thus are tagged with the Field stereotype).

**Field**

A Field is a subelement of a Form that denotes a typed value acquired from or displayed to the user.

Fields also represent Parameters for passing their values to other IFML elements. There are two kinds of fields: SimpleFields and SelectionFields.

**SimpleField**

A SimpleField is a kind of Field that captures a typed value. Such a value is typically entered by the user but can also be designated read-only or even hidden. The value of a SimpleField is an output Parameter that can be passed to other ViewElements or Actions.

As customary in data entry applications, form fields could also allow a quicker and more controlled type of interaction (e.g., the selection of values from a predefined set). This feature is captured by the SelectionField element.

**SelectionField**

A SelectionField is a kind of Field that enables the choice of one or more values from a predefined set.

Figure 5.13 shows an example of a Form with two SimpleFields and one SelectionField.
The mock-up rendition of Figure 5.13 hints at the fact that the type of the field can be used by the developer or by a code generation tool to produce the most appropriate interaction widget within the form.
Both simple and selection fields can be preloaded with values. Each Field also defines an input parameter of the Form that contains it so that its value can be preloaded with a value supplied by another IFML element. Alternatively, the provenance of the Field content can be expressed with a ContentBinding, if the content is extracted from domain model objects. Preloaded Fields behave as follow: a preloaded SimpleField displays a value to the user, who can overwrite it; a preloaded SelectionField displays multiple values to the user, who can choose the one(s) to submit. Each field also defines an output parameter of the Form that contains it, which assumes as value the entered value (for a SimpleField) or the selected value(s) (for a SelectionField) provided by the user.

Forms support interaction for submitting the content of their Fields. The basic data submission activity of the user can be represented by an extension of the generic Event construct called SubmitEvent.

**SubmitEvent**

A SubmitEvent is a kind of event that denotes the submission of one or more values. It triggers the Parameter passing from the ViewComponent owning the event to the ViewComponent or Action target of the NavigationFlow outgoing from the event.

Figure 5.14 shows an example of Form ViewComponent with one SimpleField and one SubmitEvent (note that the SubmitEvent is represented by an “enter button” icon). The “MessageKeywordSearch” Form ViewComponent is associated with the “SearchKey” SimpleField and with the “Search mail” SubmitEvent. The latter triggers an interaction that leads to the display of the “MessageList” ViewComponent, which publishes the messages that contain the search keyword in their title. The OCL expression that selects the set of instances whose title contains the input keyword is:
```ocl
if (keyword.size() <= title.size()) then
 Sequence(1..title.size()- Keyword.size()) -> exists(i|
 title.substring(i,i+Keyword.size()) = Keyword)
 else
 false
```
which checks that the input keyword is a substring of the message title.

### Content and Navigation Patterns and Practices

As already mentioned in chapter 4, interface design patterns are IFML models that embody the solution to recurrent interface design problems. In the following, we discuss useful patterns that emerge frequently during the design of the content and interactivity of the user interface. The patterns described in this chapter are high level and platform independent. Platform-specific patterns are discussed in chapter 7.
We start by introducing content and navigation patterns, reusable models that effectively addresses a recurrent set of requirements in the design of the content and navigation in user interfaces. We prefix the name of platform-independent content and navigation patterns with CN.

#### PATTERN CN-MD: Master Detail and PATTERN CN-MMD: Master Multidetail

The master detail pattern is the simplest data access pattern, already exemplified in Figure 5.11. A List ViewComponent is used to present some instances (the so-called master list), and a selection Event permits the user to access the details of one instance at a time. The master multidetail variant occurs when the object selected in the master list is published with more than one ViewComponents, as shown in Figure 5.9.

#### PATTERN CN-MLMD: Multilevel Master Detail

This pattern, sometimes also called “cascaded index,” consists of a sequence of List ViewComponents defined over distinct classes, such that each List specifies a change of focus from one object (selected from the index) to the set of objects related to it via an association role. In the end, a single object is shown in a Details ViewComponent, or several objects are shown in a List ViewComponent. A typical usage of the pattern exploits one or more data access classes to build a navigation path to the instances of a core class. For example, Figure 2.2 provides an example of the multilevel master detail pattern exploiting the instances of the “Category” access class to access the instances of the “Product” core class.

#### PATTERN CN-DEF: Default Selection

A usability principle suggests maximizing the stability of the interface by avoiding abrupt and far reaching changes of the view when they are not necessary. The default selection pattern helps improve the stability of interfaces that show pieces of correlated content and allow the user to make choices.

The basic master detail pattern and the multilevel master detail pattern exhibit possibly unwanted interface instability, as visible in Figure 5.3. When the ViewContainer is initially accessed, the first List ViewComponent is computed and appears rendered in the interface. However, the Details or List ViewComponent, which depends on a parameter value supplied by a user selection, cannot be computed, and thus the interface contains an “empty hole” corresponding to it. When the user selects one item from the list, then the missing parameter value becomes available and the content of the second ViewComponent can be computed, thus filling the hole but producing a possibly unwanted instability of the interface.
The default selection pattern resolves this problem by simulating a user selection at the initial access of the ViewContainer. A default value is chosen from the source ViewComponent and used to define the value of the parameter needed for computing the target ViewComponent. In this way, the user sees a stable interface initialized with a system-defined object or list, which the user can subsequently change by using the provided interactive events.
Figure 5.15 shows the notation for expressing the default selection pattern.
Besides the NavigationFlow outgoing from the select event, the pattern also includes a DataFlow, which expresses a parameter passing rule for supplying a default value when the page is accessed, in absence of user interaction.

### Data Entry Patterns

Data entry is one of the most important activities supported by the front end and one where usability requirements are most stringent. In the next sections, we illustrate some cross-platform patterns generally applicable to data entry interfaces, based on the usage of Form ViewComponents. We prefix the name of platform-independent data entry patterns with DE.

#### PATTERN DE-FRM: Multifield Forms

The basic data entry pattern consists of a Form ViewComponent with several fields corresponding to such elements as the properties of an object to be created or updated, the criteria for searching a repository, or the parameter values to be sent to an external service.

Figure 5.16 shows an example of multi-field form for composing an e-mail message.
As Figure 5.16 illustrates, assigning a type with the fields adds useful information to the model. For example, a code generator may render a text editing field by means of a rich text editing widget or a Blob field with a file chooser window. Other examples are Boolean fields rendered as radio buttons and date fields rendered as calendars. We will show how to extend Fields to specify several usability hints in chapter 8.

#### PATTERN DE-PLDF: Preloaded Field

In many situations, the data entered in a form modify or add to existing information. Examples include updating the description of a product in an online e-commerce web site or changing one’s profile in a social network. In each case, preloading fields with content augments the usability of the interface and reduces data entry errors.

Figure 5.17 shows the pattern for preloading a SimpleField and a SelectionField in two different ways. The “Categories” SelectionField incorporates a DataBinding element, which specifies that the values are extracted from the “name” attribute of the “Category” objects of the domain model. Conversely, the “Description” SimpleField is preloaded by means of a ParameterBinding associated with the DataFlow connecting the “ProductDetails” Form and the “UpdateProduct” ViewComponents. In this way, the text of the description attribute of the product object in display is also used to provide an initial value to the homonymous field in the Form.

Figure 5.18 shows another example of field preloading: a form for replying to an existing e-mail message, in which the fields of the new message are partly preloaded with the values of the original message. The “Reply” event associates the subject of the original message to the subject of the new message prefixed with the string “Re: ,” copies the recipient of the original message into the sender of the new message, and pulls the body of the original message into the body of the new message.

#### PATTERN DE-PASF: Preassigned Selection Field

This design pattern helps when the user’s selection among a number of different choices can be inferred from available information (e.g., from profile data, previous choices, or the interaction context). In this case, the value of a SelectionField can be initialized with a ParameterBinding, as shown in Figure 5.19.
The “SignUp” ViewContainer shown in Figure 5.19 contains a “UserCountry” Details ViewComponent that retrieves the default country for a user by querying the Locale contextVariable and exposes an OutputParameter UserCountry. Such a piece of information is passed to the form “SignUp” as input parameter CountryPreselect to set the value of the “Country” SelectionField. Note the use of a DataFlow from the Details to the Form because no interaction is required except the association of the parameter with the SelectionField parameter value.

#### PATTERN DE-DLKP: Data Lookup

This design pattern is useful when the data entry task involves a complex form with choices among many options, such as in the case of form filling with large product catalogues. In this case, a SelectionField can be conveniently supported by a data lookup ViewContainer, which contains a data access pattern such as a master details.

Figure 5.20 shows an example of data lookup. The “FillRequest” Form contains a SimpleField “ProductCode” that must be filled with the code of a product. An event “Pick” opens a ViewContainer (e,g, a modal window) whereby the user can navigate the product taxonomy and select the desired code. The product code chosen with the data lookup is assigned to the SimpleField “ProductCode” using a ParameterBinding.

#### PATTERN DE-CSF: Cascade Selection Fields

The cascade selection field pattern is useful when the data entry task involves entering a set of selections that have some kind of dependency. The typical example is a form for entering user information, where the address is incrementally built by selecting the country, the state or province, and then the city. If this step by step selection is performed within a form with selection fields, the fields need to be dynamically updated according to the selection at the previous step. In this case, the list of states or provinces depends on the selected country, and the list of cities depends on the selected province. Figure 5.21 shows the IFML model that exemplifies this behavior. The selection of an element in the “Country” SelectionField triggers the calculation of the list of associated states to be shown in the “State” SelectionField.

#### PATTERN DE-WIZ: Wizard

The wizard design pattern supports the partition of a data entry procedure into logical steps that must be followed in a predetermined sequence. Depending on the step reached, the user can move forward or backward without losing the partial selections made up to that point. Figure 5.22 shows a three-step wizard.
Notice that at each step the Form ViewComponent shows one Field, the one pertinent to the current step, and caches the values of the inputs of all steps in Parameters. The events and navigation flows for moving from one step to another are associated with a ParameterBinding that carries the current values of all the fields to keep track of interactions performed in previous steps. In this way, the user can go back and forth and—at the end—all the collected values are correctly submitted.

An alternative equivalent design can be that of associating a single copy of all the wizard parameters with the enclosing ViewContainer and updating such global parameters at each previous/next event.

### Search Patterns

Search patterns address recurrent problems in which user input must be matched against some content to retrieve relevant information. We prefix the name of platform-independent content search patterns with CS.

#### PATTERN CS-SRC: Basic Search

The basic search pattern has already been exemplified in Figure 5.14, where a Form ViewComponent with one SimpleField is used to input a search key. This key is used as the value of a parameter in the ConditionalExpression of a List ViewComponent that displays all the instances of a class that contain the keyword. A variant of the pattern that searches the keyword in multiple attributes of the target class is obtained using disjunctive subclauses in the ConditionalExpression:
```ocl
if (keyword.size() <= title.size()) then
 Sequence(1..title.size() - Keyword.size()) -> c(i|
 title.substring(i, i + Keyword.size()) = Keyword)
 else
 false
```
OR
```ocl
if (keyword.size() <= body.size()) then
 Sequence(1..body.size() - Keyword.size()) -> exists(i|
 body.substring(i, i + Keyword.size()) = Keyword)
 else
 false
```
With the above expression, the keyword is searched in the title or in the body of a message.

#### PATTERN CS-MCS: Multicriteria Search

The advanced multicriteria search pattern uses a Form ViewComponent with multiple Fields to express a composite search criterion. Figure 5.23 shows an example of multicriteria search pattern. The “Message full search” Form contains multiple Field elements for the user to fill. A ParameterBindingGroup assigns the field values to the parameters in the ConditionalExpression of the “MessageList” ViewComponent.

#### PATTERN CS-FSR: Faceted Search

Faceted search is a modality of information retrieval particularly well suited to structured multidimensional data. It is used to allow the progressive refinement of the search results by restricting the objects that match the query based on their properties, called facets. By selecting one or more values of some of the facets, the result set is narrowed down to only those objects that possess the selected values. Figure 5.24 shows an example of faceted search applied to bibliography information retrieval.
The model of Figure 5.24 consists of a ViewContainer (“FacetedSearch”), which comprises a Form for entering the search keywords, a List for showing the query matches (“Results”), and two MultiChoice Lists (“Years” and “Venues”) for selecting facet values and restricting the result set. At the first access of the ViewContainer, no keyword has been provided yet by the user, and thus the ConditionalExpression of the “Results” List evaluates to false and the ViewComponent is not displayed. The same holds for the “Years” and “Venues” ViewComponents (their ConditionalExpressions are not entirely shown in Figure 5.24 for space reasons, but they retrieve the documents that match the input keyword). When the user submits a keyword and triggers the “Search” event, the ConditionalExpressions of the “Results,” “Years,” and “Venues” ViewComponents are evaluated and the content of these ViewComponents is populated with the matching documents. The VisualizationAttributes of the “Years” and “Venues” ViewComponents comprise a single attribute, whose distinct values are displayed as facets1. Checking or unchecking the values of the facets triggers the corresponding events shown in Figure 5.24, which causes the binding of the “Years” and “Venues” parameters. As a consequence, the ConditionalExpression of the “Results” ViewComponent is evaluated using those parameters, which—if not empty—can lead to the restriction of the result set.

### Running Example

As already mentioned in chapter 4, the e-mail application interface consists of a top-level ViewContainer, which is logically divided into two alternative subcontainers: one for managing mail messages (open by default when the application is accessed) and one for managing contacts.
The “Messages” ViewContainer, visible in Figure 5.25, displays the list of the available mailboxes, which is presented in conjunction with the messages contained in a mailbox or with the interface for composing a message or for editing the mail settings. Selecting a mailbox causes the messages it contains to appear in the central part of the interface (the MailBox sub-ViewContainer). Entering the application causes the selection of a default mailbox in accordance with PATTERN CN-DEF: default selection.
Figure 5.26 shows the ViewComponents, Event, and NavigationFlow that model the selection and display of a mailbox.
Access to the messages can also occur through a search functionality displayed together with the mailbox list. An input field supports simple keyword based search. With a click, the user can access an alternative full-search input form that allows the entry of various criteria, as shown in Figure 5.27.
Figure 5.28 shows the model of the two alternate search functions. A modeless ViewContainer is used to denote that the full search form opens in a modeless window, as shown in Figure 5.27. The forms “Message Keyword search” and “Full Search” contain the fields shown in Figure 5.14 and Figure 5.23, respectively. The “Message List” ViewComponent has three ConditionalExpressions. Each expression is reached by a navigation flow, one for each of the ways in which it can be accessed. At every user interaction, only the expression that is the target of the current user navigation will be evaluated. The condition expressions are visible in Figure 5.14, Figure 5.23, and Figure 5.26.
For brevity, Figure 5.28 omits representation of the ParameterBindingGroup elements associated with the events “Select Mailbox,” “Search mail,” and “Search mail full.”
Figure 5.28 also shows a refinement of the “MailBox” ViewContainer, which unveils its internal organization into the sub-ViewContainers necessary to alternate between the visualization of a message list and that of a single message. The “MessageList” ViewComponent supports interaction with mail messages individually or in sets. On the entire set of messages, the “MarkAllAsRead” event permits the user to update all the messages in the current MailBox, setting their status to “read” (see Figure 5.29).
As shown in Figure 5.30, the “MessageList” ViewComponent also supports a second kind of interaction, the selection of a subset of messages. When at least one message is selected, a ViewContainer is displayed (“MessageToolbar”), which permits the user to perform several actions on the selected message(s), including archiving, deleting, moving to a MailBox/Tag, and reporting as spam.
When one or more messages are selected in the “MessageList” ViewComponent, the “MessageToolbar” view container appears, which allows the user to perform several actions on the selected messages. If all messages are deselected, such a view container disappears
In summary, the “MessageList” ViewComponent supports three types of interactive events:

1. An event for selecting the entire set of messages and triggering an action upon them, marking all messages as read (Figure 5.29);
2. Two events for checking/unchecking messages (Figure 5.30);
3. An event for selecting an individual message and opening it for reading.

The Events of the “MessageList” ViewComponent are modeled in Figure 5.31 and Figure 5.33.
The “SelectMultiple” checking event marks one or more messages in the current mailbox and produces the display of the “MessageToolbar” ViewContainer, which remains active while at least one message is selected. The “Deselect” unchecking event allows the user to deselect messages, which updates the value of the “MessageSet” parameter. Notice that the checking and unchecking events are triggered every time one element is checked or unchecked in the list. The “SelectMultiple” event has a ParameterBinding, which associates the (possibly empty) set of currently selected messages with an input parameter of the “MessageToolbar” ViewContainer. The “MessageToolbar” ViewContainer is also associated with an ActivationExpression, which verifies that at least one message is selected. The “SelectOne” SelectEvent enables the selection of a single message from the mailbox and causes the details of the message to be displayed, as shown in the mock-up of Figure 5.32.
This functionality is modeled in Figure 5.33 with a SelectEvent associated with the “MessageList” ViewComponent, which causes the setting of the “MessageSet” parameter and the display of the “MessageReader” ViewComponent. Such a component permits the user to access one specific message at a time. Its visualization replaces the “MessageList” ViewContainer, as denote by the XOR nesting of the children ViewContainers “MessageList” and “MessageDetails” within “MessageViewer,” shown in Figure 5.31 and Figure 5.33.
We conclude this elaborate example with a model of the functionality for composing messages. The interface for composing a message can be accessed in two ways: by clicking on the “Compose” link anywhere in the message management interface (to write a new message) and by selecting one of the various commands available in the message reader interface (for replying to or forwarding an existing message). Consequently, the model should support both the content-independent and the content-dependent navigation to the message composer. Figure 5.34 shows the mock-ups of the two ways for accessing the message composer functionality; notice that the content of the message editing fields and the navigation events available differ in the two cases.
Figure 5.31 and Figure 5.33 show the model of content-independent navigation that permits the user to access the message writing functionality. The “MessageWriter” ViewContainer is marked as landmark, and therefore it is accessible from all the other ViewContainers of the “MessageManagement” ViewContainer. It contains the “MessageComposer” ViewComponent, modeled as a form with different fields corresponding to the main attributes and relationships of the domain model class “Message”: To, Cc, Bcc, Subject, Body, and Attachment. When the “MessageWriter” ViewComponent is accessed in the content-independent navigation case, the form fields are not preloaded and the user can fill them freely, as shown in the left part of Figure 5.34.
Conversely, Figure 5.35 shows the model expressing the access to the message composer functionality as a consequence of content-dependent navigation. The “MessageReader” ViewComponent is associated with three events (“Reply,” “ReplyToAll,” and “Forward”) that allow the user to navigate to the “MessageWriter” ViewContainer and access the “MessageComposer” Form. The “ReplyToAll” event is active only when the message displayed in the “MessageReader” ViewComponent has more than one recipients, as expressed by the activation expression associated with the “ReplyToAll” event.
The “Reply,” “ReplyToAll,” and “Forward” events are associated with a ParameterBindingGroup, which conveys the properties of the original message displayed in the “MessageReader” ViewComponent. These properties are used to preload the fields of the “MessageComposer” Form as shown in the mock-up in Figure 5.34 (right). Each form field is associated with a parameter of the same name, which takes a value from the proper attribute of the original message as expressed by the ParameterBindingGroup:
- The “Reply” and “ReplyAll” events associate the subject of the original message with the subject of the new message (prefixed with the string “Re: “), the recipient of the original message with the sender of the new message, the body and the cc recipients of the original message to the body and cc recipients of the new message.

- The “Forward” event associates the subject of the original message with the subject of the new message (prefixed with the string “Fw: ”) and the body of the original message with the body the new message.

The “MessageComposer” Form supports two SubmitEvents (“Send” and “Save”) for sending and for saving without sending the message, respectively.

The “MessageComposer” Form, whose mock-up appears in Figure 5.34, also supports a kind of stateful interaction. Besides the events “AddCc,” “AddBcc,” “AddAttachment”—which are available irrespective of the kind of response the user is editing—the events “Reply,” “ReplyToAll,” and “Forward,” allow switching the response type. However, only two out the three events are active at a time depending on the current state of the editing. For example, when the user is editing a “ReplyToAll” message, only the “Reply,” and “Forward” events are active. This is conveyed by the “State” parameter of the Form and by the three ActivationExpressions associated with the events, as shown in Figure 5.36. The ActivationExpressions check for the value of the parameter “State,” which is set appropriately by each of the “Reply,” “ReplyToAll,” and “Forward” events, so that only the events appropriate to the current editing context are active.
Another example of a conditional event is the “EditSubject” Event. The event for editing the subject field is disabled when the value of the “State” parameter is “Forward.”

## Modeling business actions

Taking the Model–View–Controller pattern as a high-level conceptual description of the way in which an interactive application works, the view allows the user to trigger events, which are handled by the controller. The controller dispatches each event to the proper element in the model, which performs the business action implied by the event. This can result in the update of the application status. At the end of the cycle, the view is updated to display the current status to the user for the next round of interaction. This typical roundtrip is shown in Figure 6.1.
The model could be logically regarded as responsible for two distinct aspects: exposing the business actions that embody the service requested by the user and maintaining the status of the application, which displays in the view.

In chapter 3, we discussed how to construct a domain model that specifies the objects of the application model. In chapter 4, we described how to define the general structure of the application interface. Chapter 5 illustrated how to express the publication of the domain objects in the interface.
The focus of this chapter is on the business logic of the application, be it embedded in methods of the application domain objects, described by suitable UML behavioral diagrams, or delegated to external objects and services.

The goal of IFML is not modeling the internal functioning of the application business logic. Rather the objective is to express the interplay between the interface and the business logic. This is done by:

- Showing that an event triggers a business action, which may imply also the specification of some input–output dependency between the interface and the business logic; and

- Showing that the interface can receive and respond to events generated by “the system,” be it a business component of the application or an external service. In this case, IFML also permits the designer to describe the input–output dependency between the information carried by a system event and the affected elements of the interface.

IFML does not replace the behavior specification languages that are normally employed to describe the algorithmic aspects of the business logic. IFML business actions are black boxes that show the minimal amount of information needed to specify the abovementioned aspects. The designer is free to focus on such black boxes and describe their internal functioning using the behavioral language of choice. To support this kind of refinement, an action in IFML can reference a behavior in an external model.

### Actions

Actions

An Action represents a reference to some business logic triggered by an Event.

Actions may reside on the server or on the client side. The elementary design pattern for triggering actions is represented in Figure 6.2.
The model contains a source ViewContainer and ViewComponent, with an Event connected via an InteractionFlow to an Action (shown as a named hexagon). The Action is itself connected to a target ViewComponent through an outgoing flow by an event typically representing the completion of the Action. ParameterBinding elements are used to denote the input–output dependency between the source ViewComponent and the Action, and between the Action and the target ViewComponent.

For example, the source ViewComponent could be a form for entering a flight request. The Action could be a flight brokering business component that takes as input the form data, checks availability and price at different flight operators, and produces the best offers as output. The target ViewComponent could be a List showing the retrieved options to the user.

The pattern of Figure 6.2 assumes that the action always terminates with the same event, after which the same target ViewContainer is displayed. However, in many situations, invoking a piece of business logic may result in various alternative outcomes lead to different termination events. Therefore, Actions may trigger different Events, called ActionEvents, as the result of the normal termination of computation or to signal the occurrence of exceptions.

ActionEvents

An ActionEvent is an Event that may be produced by an Action to signal normal or exceptional termination.

Figure 6.3 shows the typical usage of multiple ActionEvents. The Action can terminate in normal or exceptional conditions, and the ActionEvents and associated InteractionFlows express the course of action taken in the two cases. For example, the source ViewComponent could be a form for signing up an application to an external service, and the Action could be a validation business component, taking as input the form data, validating it, and producing a limited-time service token. In case of normal termination, the target ViewComponent could be a Details component showing the newly generated token and the service terms and conditions to the user. Exceptional termination may also occur (e.g., when the user’s request does not meet the conditions for obtaining an access token). In this case, the target ViewComponent could be a Details component showing the reasons of failure to the user.
The source and the target ViewComponent of an action invocation need not be distinct. For example, Figure 6.4 shows a model of an interface for deleting objects from a list. The source ViewComponent allows the user to select an object for deletion. After the deletion, the same ViewComponent is presented again with its content updated.
Figure 6.4 also shows two shortcuts for simplifying the ActionEvent notation. When no outgoing InteractionFlow and no ActionEvent are associated with the Action, it is assumed that the target is the smallest ViewContainer comprising the source ViewElement from which the Action has been activated.

### Notification

The influence of business logic on the interface manifests not only when the user takes the initiative but also as a consequence of a system-initiated action. This situation requires modeling the notification of an occurrence from the application back end of an external system to the user interface. In this case, the IFML model does not represent the initiation and execution of the action but only its ultimate effect, which is captured by a SystemEvent.

**SystemEvent and SystemFlow**

A SystemEvent is an Event produced by the system that triggers a computation reflected in the user interface. Examples of SystemEvents are time events (which are triggered after an elapsed frame of time), system alerts (such as a database connection loss), or message receipt notifications.

A SystemFlow is an InteractionFlow that connects a SystemEvent to a ViewElement to identify the element affected by the occurrence of the SystemEvent.

The cause of a SystemEvent may be left unspecified in the model, although it is also possible to express a condition whose occurrence triggers the SystemEvent. Such a condition is represented by means of a TriggeringExpression.

**TriggeringExpression**

A TriggeringExpression is an expression that determines when or under what conditions a SystemEvent should be triggered.

The notification PATTERN A-notif, introduced later in this chapter, contains an example of a SystemEvent, a SystemFlow, and a TriggeringExpression.

### Business Action Patterns

Several design patterns embody the solution to recurrent problems in the design of the interplay between the user interface and the business logic. We call such platform-independent patterns action patterns and prefix their name with an “A.”

#### Content Management Patterns

The most important action patterns relate to the management of the objects of the domain model. Such content management patterns all have a similar structure. They exploit an Action endowed with the input parameters necessary to create, delete, or modify objects and association instances, and with output parameters that characterize the effect of the performed content update. The role of the interface is that of supplying the input and of visualizing the output to the user as a confirmation that the action has been executed and the application state updated.

#### PATTERN A-OCR: Object Creation

The object creation pattern enables the creation of a new object. The pattern relies on an Action characterized by:

- a reference to the dynamic behavior that the action must perform; and

- a set of input parameters, used to initialize the attributes of the object to be created.

The input of the Action is typically supplied by a ParameterBindingGroup associated with a NavigationFlow exiting from a Form ViewComponent. The parameter values are used to construct the new object. If some attributes have no associated input value, they are set to null. The only exception is the object identifier (OID), which is normally treated in an ad hoc way: if no value is supplied, a new unique value is generated by the Action. The behavior of the object creation Action typically consists of invoking a class constructor or a factory method in a creator class. The output produced by the Action is the newly created object, comprising its OID and all its attribute values. The output of the Action is defined only when the operation succeeds and thus can be associated as a ParameterBindingGroup only with the InteractionFlow that denotes normal termination. If no ParameterBindingGroup is specified explicitly, a default output ParameterBinding consisting of the OID of the newly created object is assumed as implicitly associated to the normal termination event.

The example of Figure 6.5 shows the typical object creation pattern, which consist of the combination of an entry Form (“EnterProductData”) providing input to an Action (“CreateProduct”) that creates a new Product by invoking the DynamicBehaviour implemented by a factory method of a creator class. The Form has several fields (e.g., “Code,” “Name,” and “Price”) for entering the respective attribute values. The field values inserted by the user are associated as explicit parameters with the NavigationFlow from the Form to the Action. In the rendition, also shown in Figure 6.5, the SubmitEvent associated with the form is displayed as a submit button, which permits the activation of the Action. The “CreateProduct” Action has two ActionEvents. Normal termination is associated with an InteractionFlow that points to the “NewProductDetails” ViewComponent and with the default output parameter (the OID of the new object). The exceptional termination event is associated with an InteractionFlow that points to a ViewContainer for displaying an error message.

#### PATTERN A-OACR: Object and Association Creation

A variant of the object creation pattern can be used to create a new object and set its associations to other objects. Figure 6.6 shows an example of such an object creation and connection pattern.
The “EnterProductData” Form contains an additional SelectionField, corresponding to the association that must be set, namely the association between Product and Category. The Category SelectionField can be preloaded with all the categories as discussed in chapter 5. The NavigationFlow triggered by the SubmitEvent “CreateNewProduct” has one additional ParameterBinding for the identifier of the selected category, which is passed as input to the Action. The Action itself can be specified either by referencing a constructor that sets the proper category for the product or by referencing a behavioral diagram (e.g., a UML sequence or activity diagram) that describes all the steps to be performed for creating the object and connecting it to a category.

#### PATTERN A-ODL: Object Deletion

The object deletion pattern is used to eliminate one or more objects of a given class. The pattern requires an Action characterized by:

- a reference to the dynamic behavior that the action must perform, which is typically the invocation of a delete operation of the database; and

- the input parameters necessary to identify the object to delete.

The input to the action is conveyed by a set of ParameterBinding elements. Normally these values are one or more primary keys, although nonkey attribute values can be used as input, and the Action encapsulates the business logic for exploiting such information to retrieve the objects to delete.

At runtime, the user typically chooses either a single object displayed by a Details ViewComponent or selected from a List ViewComponent, or a set of objects chosen from a MultiChoice List ViewComponent. The identifiers of the chosen objects are associated by a ParameterBindingGroup to the NavigationFlow exiting the ViewComponent and pointing to the Action that actually deletes the objects.

Normal termination occurs when all the objects have been deleted. In this case, the Action has no output parameters. Exceptional termination occurs when at least one of the objects has not been deleted. In this case, the Action has an output parameter holding the OIDs of the objects that were not deleted. This can be useful to display the list of items that could not be deleted, together with an error message.

The example of Figure 6.7 illustrates the object deletion pattern applied to a single object. The ViewContainer includes the “ProductsList” ViewComponent connected to the “DeleteProduct” Action. The NavigationFlow has a default parameter holding the OID of the selected product, which is used in the Action. The SelectEvent fires the deletion of the chosen object. If the operation succeeds, the “Products” ViewContainer is redisplayed, but the deleted product no longer appears. In case of failure, a different ViewContainer with an error message is displayed, which may use the information about the object whose deletion failed and any other useful parameter returned by the action (e.g., a human-readable explanation of the failure).
The example of Figure 6.8 shows a variant of the object deletion patterns in which a multichoice list ViewComponent is used to let the user check a set of products and invoke the deletion Action on them. In this case, the default ParameterBinding associated with the “Delete” event of the “ProductList” ViewComponent holds the set of OIDs of the selected objects. These are displayed in the “SelectedProducts” List ViewComponent, which is associated with the “Confirm” event.
The NavigationFlow of the Delete set selection event has as default ParameterBinding that includes the entire set of objects output by the source List ViewComponent (“SelectedProducts” in this case) and triggers the “DelectedProduct” action on all the objects bound to the event.

#### PATTERN A-CODL: Cascaded Deletion

The cascaded deletion pattern allows one to remove a specific object and all the objects associated with it via one or more associations. In this case, the action is implemented by a sequence formed by two or more delete operations, one for removing the main object and the others for removing the related objects (at least one). In particular, cascaded deletion is used to propagate the deletion of an object to other dependent objects, which are connected to it by an association with minimum cardinality of 1, and thus could not exist without the object to which they refer. An example of such a situation is illustrated in Figure 6.9, which shows the use of the pattern for deleting an e-mail message and all its attachment. The “MessageDetails” ViewContainer includes a Details ViewComponent (“Message”) showing the message, and a List ViewComponent (“Attachments”) displaying its attachments. The “Message” ViewComponent is associated with an event that triggers the “CascadeDelete” Action, which conceptually consists of a sequence of two operations, deleting both the attachment and the e-mail message. The internal structure of the Action is not specified in IFML and can be described by means of a behavioral diagram. For example, Figure 6.10 specifies the cascade deletion using a UML sequence diagram. An alternative Action design could exploit the native referential integrity mechanism of the underlying data store (for example, the ON DELETE CASCADE clause of SQL foreign key constraints) and delete only the message object, leaving to the database the task of cascading the deletion.
The pattern of Figure 6.9 is a good illustration of the intertwining between the business logic and the interface design. The NavigationFlow denoting the normal termination of the “CascadeDelete” Action does not lead back to the source ViewContainer but instead to the “MessageList” ViewContainer, which is the default subcontainer of the enclosing “MessageDetails” ViewContainer. This is because the object that was displayed in the “MessageDetails” ViewComponent (the deleted message) no longer exists, and it would make no sense to redisplay it. The IFML model is the right place to express this kind of relationship between the semantics of actions and their effect in the interface.
The resulting interaction is shown in the mock-up of Figure 6.11.

#### PATTERN A-OM: Object Modification

The object modification pattern is used to update one or more objects of a given class. An object modification pattern uses an Action that is characterized by:

- the reference to the dynamic behavior that the action must perform, which is typically the invocation of a setter method; and

- the input parameters necessary to identify the object(s) to modify and to supply new values to their attributes.

When the user chooses multiple objects at runtime, the same update applies to all the selected objects. The Action must be properly linked to ViewComponents of the interface, to obtain the needed inputs.
- The new attribute values: these are typically defined as a ParameterBindingGroup associated with a NavigationFlow coming from a Form ViewComponent.

- The objects to modify: these are usually specified as a ParameterBindingGroup holding one OID or a set of OIDs.

- As an alternative to the usage of object identifiers as parameters, the objects to modify can be retrieved by the Action based on logical criteria, exploiting the values associated as parameters with InteractionFlows incoming to the Action. In this case, the Action encapsulates the object retrieval business logic.

The normal termination of the Action occurs when all the objects have been successfully modified. In this, case the ActionEvent is associated with a default parameter holding the set of OIDs of the modified objects. An exceptional termination occurs when at least one of the objects could not be modified. In that case, the ActionEvent is associated with a default parameter holding set of OIDs of the objects that were not modified.

The example of Figure 6.12 shows a Form ViewComponent used to supply values to an object modification Action. The “ProductEditor” ViewContainer comprises a Details ViewComponent (“Product”), which shows the name of the product to modify, and a Form (“EnterProductData”), whereby the user can modify the existing product attribute values. A DataFlow from the Details ViewComponent to the Action has a default parameter holding the OID of the product to modify, which is used by the Action to identify the instance to update. The Action is activated by a SubmitEvent associated with the Form. The NavigationFlow has a ParameterBindingGroup element, which associates the value of the fields of the Form with corresponding input parameters of the Action. The normal termination leads to the “UpdatedProduct” ViewContainer, which shows the modified values of the product attributes. The exceptional termination points “back” to the “ProductEditor” ViewContainer, which redisplays the old values.
Note that for classes with many attributes, the specification of the pattern can be cumbersome due to the need to repeat the relevant attributes twice: once as form fields and once in the parameter binding. However, a tool such as the one described in chapter 11 can easily provide a wizard for building the pattern with less effort (e.g., by inserting all the class attributes in the model automatically).
The example of Figure 6.13 illustrates the modification of a set of objects. The “MessageList” multichoice List is associated with a SelectEvent (“MarkAsRead”) for updating the status of the chosen messages, marking them as “read.” The outgoing NavigationFlow of the event is associated with a ParameterBindingGroup that holds the OIDs of the objects selected in the multichoice list and a constant value (“read”) for updating the status of the messages. The operation succeeds if the modification can be applied to all the objects chosen from the list, in which case the normal termination ActionEvent is raised. After this event, the “Messages” ViewContainer is redisplayed, with a notification of the number of marked messages.
The Action fails if the modification cannot be applied to some of the selected messages, which causes the exceptional termination ActionEvent to be raised and an modeless alert window to be displayed.

#### PATTERN A-AM: Association Management

An association management pattern is about maintaining the instances of associations specified in the domain model. Specifically, it is used to create/replace/delete instances of an association by connecting and/or disconnecting some objects of the source and target classes. The association management pattern exploits an Action characterized by:

- the reference to the dynamic behavior that the action must perform, which is typically the invocation of a setter method acting on the attribute that implements the association in one or in both classes; and

- input parameters for locating the objects of the source class and of the target class.

The Action is triggered by a NavigationFlow and receives as input pairs of objects of the source and target classes, identified by the ParameterBindingGroup of the NavigationFlow. It provides as output the pairs of OIDs corresponding to the objects of the source and of the target class for which an association instance has been created/replaced/deleted. These values can be used to define a ParameterBindingGroup associated with the normal and exceptional termination ActionEvents. The latter is raised when the management of at least one association instance fails, whereas the normal termination ActionEvent signals that all the association instances have been managed properly.
Figure 6.14 shows an example of the association management pattern for updating the category of a product, which corresponds to a one-to-many association in the domain model. The “Product” Details ViewComponent in the “ProductCategories” ViewContainer displays a current product, as the result of a previous selection in another ViewContainer (not shown in Figure 6.14). The ViewContainer also includes the “CurrentCategory” Details ViewComponent, which displays the category of the displayed product. The primary key of the displayed product—necessary for determining the actual category in the “CurrentCategory” ViewComponent—is supplied by a ParameterBindingGroup associated with the DataFlow from the “Product” to the “CurrentCategory” ViewComponent.
Finally, the “ProductCategories” ViewContainer comprises a List ViewComponent (“Categories”) showing all the categories from which the user can select the desired one and trigger the “Assign” SubmitEvent. This event triggers the Action for updating the relationship instance between the displayed product, whose primary key is supplied by a DataFlow with a ParameterBindingGroup, and the new category selected from the list. The normal termination event of the Action causes the “ProductCategories” ViewContainer to be redisplayed, showing the updated category of the product. In case of abnormal termination, an Alert window is presented before letting the user go back to the original ViewContainer.

#### PATTERN A-notif: Notification

This pattern models the case in which the interface is (typically asynchronously) updated by the occurrence of a system generated event. Figure 6.15 shows an example of the notification pattern.
In the e-mail application, actions on messages (such as sending, deleting, and moving to a different folder) are triggered by an Event and executed by an Action at the server side. When the action terminates, the system produces a completion event and sends an asynchronous notification to the interface. The effect of catching a notification event is represented by a SystemEvent, which triggers the display of a “MessageNotification” ViewComponent, as shown in Figure 6.15.
The production of a SystemEvent can be left undetermined, in which case it is assumed that the system sends the event in a completely unspecified manner, or be associated with an Action of the interface model to convey that the notification is connected with the termination of an Action. For example, all the notification events of the e-mail application can be associated with the termination of the respective Action, as shown in Figure 6.16.

### Running Example

The e-mail application allows the users to perform a variety of operations on messages, including composing a new message, replying to a received message, and moving a message to a new or to an existing folder. When one or more messages are selected, they can be moved to another folder by means of the “MoveTo” command.

Figure 6.17 shows the mock-up of interface supporting a command. A ViewContainer is displayed in a new window with the list of available MailBox and Tags. The user can select from such a list the destination Folder to which he wants to move the messages. This functionality can be modeled with an instance of PATTERN A-AM: Association management, shown in Figure 6.18: the “MessageToolbar” ViewContainer is associated with the “MoveTo” Event, which causes the display of the “Chooser” modeless window. This ViewContainer comprises a list for selecting the target folder. The selection event triggers the “MoveTo” Action that performs the command and sends a notification event upon termination, which is captured by the “MessageNotification” ViewComponent in the top-level container (as already illustrated in Figure 6.15).
Note that in this example of association management pattern, the messages to move are associated as a ParameterBinding to a DataFlow that connects the “MessageToolbar” ViewContainer to the Action, whereas the OID of the destination folder is associated by default with the NavigationFlow of the “Select” Event and thus omitted from the diagram.
As visible in the mock-up of Figure 6.17, the window for choosing the target folder also contains a command for creating a new folder that opens a modal window for entering the name and parent folder of the new folder. Figure 6.19 shows the mock-up of this functionality.
The model including the functionality for moving a message to a newly created folder is shown in Figure 6.20. The “CreateNew” event associated with the “Chooser” ViewContainer opens a modal ViewContainer with the form for entering the name of the new folder (using a SimpleField) and selecting the parent folders (using a SelectionField). The “Create” Event in the modal window triggers an Action for creating the new folder and associating it to the specified parent folder and to the messages selected previously. Upon normal termination, the Action emits a notification message.
Besides the commands for moving messages, the toolbar provides functionality for archiving, reporting, and deleting message. Figure 6.21 completes the partial model viewed so far with the remaining Actions.
An additional note concerning the allocation of the business logic to the architectural tiers of the application is needed. So far, the illustration has been purposely neutral as to where an Action is executed within the architecture of the application, because the platform-independent model should not incorporate unnecessary architectural assumptions. However, this does not mean that all actions are executed on the same tier or that only server-side business logic can be modeled. To illustrate this aspect, we conclude the running example with an expansion of the model of the message composition functionality, already described in chapter 5.
The model of the “MessageWriter” ViewComponent can be refined by zooming in inside the “Body” field, which supports client-side business logic (such as rich formatting of the text) and mixed server- and client-side functionality (such as spellchecking). Figure 6.22 shows a mock-up of this functionality.
The embedding of a full-fledged microapplication such as a rich text editor inside a Form ViewComponent can be modeled by replacing the SimpleField with a more complex ViewComponentPart called RichTextEditor, as shown in Figure 6.23. Such ViewComponentPart could support events and further nested ViewComponentParts as required to express its interface. The execution tier of an Action could also be expressed as a stereotype. For example, Figure 6.23 tags the Actions executed at client side with an appropriate stereotype.

## IFML extensions

The IFML standard comes organized as a core set of concepts and a number of extensions that embody general characteristics found in many interactive applications. The extension mechanism applies to all the main concepts of IFML. The extensions included in the standard are:
- ViewContainer extensions: Window
- ViewComponent and ViewComponent Part extensions: Details, Field, Form, List, SelectionField, SimpleField, Slot
- Event extensions: SelectEvent, SubmitEvent, SystemEvent
- ContextDimension extensions: Device, Position, UserRole
- Expression extensions: ValidationRule
Further custom extensions are allowed for the main concepts of IFML: ViewContainers, ViewComponents, ViewComponentParts, Events, and domain and behavior concepts (and their extensions).
The purposes of extensions are manifold:
- Adding expressive power to the modeling language;
- Making the concepts and notation less abstract and closer to the intuition of designers;
- Allowing different specialized concepts to be distinguishable visually, for improved readability of diagrams; and
- Assigning more precise meaning to concepts to enable deeper model checking, formalization of semantics, and executability (through code generation or model interpretation).
Figure 7.1 shows the use of IFML extensions (equipped with customized icons) for making the visual notation more intuitive, enabling model checking, and supporting code generation. This example will be expanded in chapter 11.
The advantages of extensibility persist and even increase when one considers IFML under the perspective of a specific category of applications that exhibit their own interface styles, technological constraints, and sometimes even peculiar terminology or jargon.
This chapter introduces several specializations of IFML that exploit extensibility to capture features found in different classes of applications, including, desktop, web, and mobile applications. The assignment of an extension to a class of application is somewhat arbitrary. The convergence of the implementation languages and platforms makes it impossible to distinguish the features of desktop, web, and mobile application sharply. For a better organization of the chapter, though, we have placed each extension under the category in which it originated or is most often or exclusively used.

### Desktop Extensions

Under the umbrella term of desktop applications we mean applications that allow the most precise control over the user interface, developed with a variety of different technologies, ranging from window-based applications developed in such technologies as Java Swing or Windows Forms to rich Internet applications implemented with JavaScript and HTML 5. Although this equivalence is imprecise from the programming point of view, it is sufficient to identify cross-platform features that are general enough to provide good candidates for IFML extensions.

#### Event Extensions

Probably, the most relevant capability of desktop applications is the very detailed management of the events that the user can generate in the interface. Therefore, an important area of extensibility of IFML regards the event types supported by desktop interfaces. These events are so numerous as to make it unfeasible to review all of them and the properties to be modeled for creating an IFML extension. Rather, we will discuss what makes an event type worth an extension and the features that should be modeled as additions to the basic notion of Event. When considering a new event type as a candidate for extension, the following questions should be addressed:
- What ViewElements can the event be associated with? ViewContainers, ViewComponents, ViewComponentParts, a specific extension of such elements, or a mix thereof?
- In there any restriction on the type of ViewElements that can be the target of the InteractionFlow associated with the event?
- What parameters can be associated with the InteractionFlow connected with the event?
Figure 7.2 shows an example of event specialization.

**OnFocusLost**

The OnFocusLost event is an extension of ViewElementEvent that captures the loss of focus of a SimpleField in a Form. The event is triggered when the user moves away from the field (e.g., by using the tab key or by clicking on another field). It can be associated with a SimpleField or with an entire Form. Its outgoing InteractionFlow can have any ViewElement as a target and a ParameterBindingGroup comprising as input parameter the value of the SimpleField or the values of all the SimpleFields of the Form.
Figure 7.2 demonstrates the usage of the OnFocusLost event to invoke Actions. In one case the event is associated with the “Username” field for checking the availability of the username provided by the user. Other OnFocusLost events are associated with other fields for auto-saving the value input by the user when the focus leaves the field.

##### Drag and Drop

The OnFocusLost event and other similar event extensions detect an atomic self-contained user interaction. Desktop applications also support more elaborate behaviors that span a sequence of interactions, such as drag and drop. A drag and drop behavior consists of the correlation of two event types: OnDragStart and OnDrop.

###### OnDragStart and OnDrop

The OnDragStart event is an extension of ViewElementEvent that captures the beginning of a drag interaction. It can be associated with Details or List ViewComponents (and specializations thereof). It has no outgoing InteractionFlow element. It has a mandatory property “OnDropEvent” that denotes an event of type OnDrop, which is the target of the OnDragStart event.
The OnDrop event is an extension of ViewElementEvent that captures the termination of a drop interaction. It can be associated with a Details or List ViewComponent (and specializations thereof). It must appear as the value of the OnDropEvent property of an event of type OnDragStart, which is the source of the OnDrop event. It has one outgoing InteractionFlow element. Such InteractionFlow can have any ViewElement as a target and a DataBindingGroup comprising two input parameters: (1) the value of one or more class instances of the ViewComponent associated with the source OnDragStart event and (2) the value of one or more class instances of the ViewComponent associated with the OnDrop target event.
As shown in Figure 7.3, the drag and drop behavior is modeled with a pair of events: one (OnDragStart) binds to the object(s) that are dragged, and the other (OnDrop) binds to the object(s) on which the dragged item(s) are dropped. These two (sets of) instances can be used as parameter values associated with the InteractionFlow exiting the OnDrop event. In the case of Figure 7.3, one or more messages are dragged from the message list of the currently open mail box and dropped on another mail box. The drop termination event triggers the “MoveTo” Action, which moves the dragged messages to the drop mail box.

#### Component Extensions

Container and component extensions add features to the basic IFML ViewElements.

##### Tree explorer

A “classic” component of desktop interfaces is the Tree component, used to display hierarchical data. Essentially, a tree is a special kind of list that displays not only objects but also their containment associations. Therefore, the data model of a tree component consists of a class, which represents the common type of the objects displayed in the tree, and a recursive association, which represents the hierarchy. In the simplest case, interaction with the tree is done by selecting one node at a time.

**Tree ViewComponent**

A Tree is an extension of the List ViewComponent that displays hierarchical data. It owns a DataBinding element that refers to a class of the domain model and a RecursiveNestedDataBinding element that refers to a one-to-many association defined on the instances of the class.
Figure 7.4 shows an example of the Tree component for publishing a selectable list of nested mailboxes. A Selection event allows the user to select one element in the tree and thus display its details.

##### Table

Another popular component of desktop applications is the table editor, also called a record set editor or data grid. The component displays a table of data and allows the user to add and delete rows and edit cell content. The data model of the component is any piece of tabular data. For simplicity we illustrate the case in which instances of a class are used as data, but alternative data bindings can be defined, as already possible with the standard concept of DataBinding. The only constraint is that the rows of the table should correspond to identifiable objects, if one wants to trap events like row deletion and therefore update the underlying data accordingly.
The Table component can be associated with such events as the update of a cell or the insertion and deletion of a row.

**Table ViewComponent**

A Table is an extension of ViewComponent that displays tabular data and allows the user to edit them. It has a DataBinding element that typically refers to a class of the domain model. The attributes of the class are mapped to the columns of the table using the ColumnAttribute ViewComponentPart. The Table component can be associated with events of type CellUpdate, RowInsertion, and RowDeletion.
Figure 7.5 shows an example of usage of the Table component for editing a record set of products. At each cell update, a data update Action “SaveProduct” is invoked with a parameter binding that holds the modified field value. The deletion of a row triggers the deletion of the corresponding class instance, identified by a parameter binding corresponding to the object displayed in the affected table row. The creation of a row invokes the creation of a new object based on the values entered in the Table row by the user. After the execution of the Actions, the Table is redisplayed with the updated content. (Recall that an InteractionFlow pointing to the source element of the action is assumed by default and thus can be omitted from the diagram).
The basic example discussed in this section can be extended, for example, with event types supporting the explicit synchronization of the table content with the data in the data store, such as “Refresh” and “SaveAll,” and with more compact parameters (e.g., representing the content of an entire row or of all the rows of the table).

#### Componentpart Extensions

Extensions can also be defined at a finer granularity, such as at the ViewComponentPart level. An example could be an editable selection field that mixes the functionality of SimpleField and SelectionField by allowing the user to edit the value of the input field or choose it from a list of options.

**EditableSelectionField**

An EditableSelectionField extends the Field element and denotes an input field that is both editable and selectable.
Figure 7.6 shows an example of usage of the EditableSelectionField extension. The “ProductCreator” form contains the “Category” EditableSelectionField that allows the user to pick the category from a list of existing categories or invent a new one. The internal business logic of the “CreateProductAndCategory” Action must distinguish whether the category is new and, if so, create the category in addition to the product. Such a behavior can be described in a separate UML diagram associated with the Action.

### Web Extensions

Web applications have brought several new concepts and an almost completely new terminology to user interface development. These are based on the fusion of previously segregated areas such as hypertext, multimedia, and form-based GUIs. The fundamental concepts of a web application are pages and links, which are borrowed from hypertext documents. Both can be viewed as specializations of core IFML concepts.

#### Container Extensions: Pages, Areas, and Site Views

In this section, we introduce IFML extensions that make the specification of the web interface composition patterns introduced in chapter 4 adhere more closely to the terminology and characteristics of web applications. The basic unit of dialogue with the user in a web application is a page, a ViewContainer produced statically by a human editor or generated automatically at the server side by a program (a page template or a server-side script). As user interfaces, pages embed navigation commands; as resources of a document system, they have a human readable address, called uniform resource locator (URL). Web applications offer service to multiple users over a multitier, client-server architecture; therefore they are concerned with the security of data transmission, achieved by delivering the interface over the HTTPS protocol, and with the control of access, achieved by enforcing user’s authentication, identification, and permission control.

**Page**

A page is an extension of ViewContainer that denotes an addressable web interface unit.
As already mentioned in chapter 4, pages in a large web application can be arranged hierarchically to facilitate user navigation.

**Area**

An Area is an extension of a disjunctive (XOR) ViewContainer that denotes a collection of pages or other areas, grouped according to an application-specific purpose.
Examples of areas in an e-commerce web application can be products, special deals, shipping rates and conditions, and returns and complaints.

As noted in chapter 4, web applications often offer different viewpoints on the same content to different classes of users. This characteristic can be captured by associating a ViewPoint with a specific type of ViewContainer called SiteView.

**SiteView**

A SiteView is an extension of a disjunctive (XOR) ViewContainer that denotes web application areas and pages grouped together according to an application-specific purpose, typically because they serve the needs of a UserRole.

In summary, a web application can be modeled as a collection of pages logically grouped into Areas and SiteViews. Pages are presented to the user one at a time. This is expressed by the disjunctive form of the enclosing ViewContainer. To express the requirements of a multiuser application, SiteViews, Areas, and Pages can be treated as resources of a role-based access control (RBAC) system. As such they can be associated with a ViewPoint, which in turn is associated with a Context, which is described, for instance, by a UserRole context dimension. The SiteView constitutes the typical item referenced by a ViewPoint. Appropriate activation rules can be defined for specifying that the SiteView is enabled for a given UserRole.
The definition of activation rules upon a SiteView/Area/Page denotes the access permission to that particular object for the specified UserRole. A SiteView/Area/Page not associated with any role is treated as public and can be accessed even when the UserRole is undetermined. In an e-commerce application, for example, different SiteViews could be associated with the UserRoles named “registered customer,” “product content manager,” and “sales manager.” A public SiteView could be addressed to nonregistered customers.
A SiteView/Area/Page has the following characteristics, which extend the standard properties of IFML ViewContainers to cope with specific web application features:
- URL label: A string denoting the (fixed part of) the SiteView/Area/Page address. If the page is implemented with a dynamic template, the URL label is typically concatenated with the parameters for the computation of its content. The URLs of a SiteView and of an Area are an alias for the home page of the SiteView and the default page of the Area.
- Security: If the property value is “secured,” all the pages of the Area or SiteView, or the individual Page, are served under the secure HTTPS protocol.
- Protection: If the property value is “protected,” all the pages of the Area or SiteView, or the individual Page, are subject to access control. The access control rule is expressed by the association of the SiteView/Area/Page with one or more UserRoles through an ActivationExpression.
Notice that the association of a UserRole with multiple levels of nesting components—such as Pages, Areas, and SiteViews—is purposely redundant and enables the incremental expression of access control rules. For example, access to a SiteView could be granted in general to the UserRoles Role1 and Role2. However, an Area or Page of the SiteView could be associated with a more restrictive ViewPoint that overrides the general one (e.g., to grant access only to Role1).
An important concept in a Web application is that of the home page, the page served to a user when accessing the application without requesting a specific resource.
Figure 7.7 reconsiders an example of web application interface organization already specified in chapter 4 using only the standard IFML concepts, and illustrates it with the concrete syntax of the described web extensions. Stereotypes are used to denote SiteViews and Pages and to identify the home page of a SiteView, as well as to determine whether the ViewContainer is Public or Protected. An ActivationExpression (e.g., Context.UserRole=”Editor”) is employed to specify that a SiteView is accessible only by a specific UserRole.

#### Event and Interaction Flow Extensions

Interaction in web applications occurs in two ways: by submitting the content of a form and by clicking on hypertext anchors. The standard IFML extensions Forms and SubmitEvent already capture the essential characteristics of web forms. The IFML NavigationFlow faithfully mirrors the concept of hypertext link but may be extended to reflect the terminology and properties of web links.

**Link**

A WebNavigationFlow is an extension of a NavigationFlow that incorporates additional properties specific to hypertext links on the web.
A WebNavigationFlow can be endowed with properties specific to web navigation:
- Rel: specifies the relationship between the current document and the linked document; its values are codified by the HTML standard.
- Target: specifies where to open the linked document, typically in a browser window; the browser window can be the same one as the original document or a new window.
Figure 7.8 shows as example of usage of the WebNavigationFlow extension used to open the licensing information in a new browser window. It also informs search engines of the nature of the linked document via the WebNavigationFlow outgoing from the technical manual to the licensing information.
The WebNavigationFlow extension shows a typical issue in the design of extensions: the tradeoff between platform independence and utility. The Rel and Target properties are clearly dependent on the version of HTML, which is an implementation language. However, a code generator could exploit the additional platform-dependent information to inject the proper attribute values in possibly thousands of automatically generated HTML links, which is an extremely useful feature. An alternative approach would factor out implementation-dependent properties from the model extensions and weave them into the code generator. However, since the values of the properties can be set by each WebNavigationFlow, in this example we prefer utility over purity and make them definable directly in the model extensions.

#### Component Extensions

The List component in the IFML standard offers a minimalistic functionality that can be extended to support more realistic interfaces.

##### Dynamically-sorted list

As illustrated in chapter 5, the OrderBy ViewComponentPart can be used to enable sorting of the items in a List ViewComponent. This compenent defines the sorting criteria (attribute plus sort direction).
Figure 7.9 shows an example taken from the running case.
The “MailBoxes” List ViewComponent has an OrderBy part that sorts instances by name, whereas the “MessageList” ViewComponent sorts its DataBinding instances by date.
The OrderBy ViewComponentPart is specified at design time and thus does not model a situation in which the user can change the sorting of data at runtime. This additional behavior, popular in both web and desktop applications, can be achieved by introducing an extension of the List ViewComponent called DynamicSortedList.

**DynamicSortedList**

The DynamicSortedList is an extension of the List ViewComponent that allows the user to sort data using visualization attributes. The DynamicSortedList has a one-to-many association, named “SortAttributes,” with the metaclass “VisualizationAttribute,” which denotes the subset of the visualization attributes usable for sorting.
Figure 7.10 shows a variant of the pattern of Figure 7.9, which uses a DynamicSortedList for displaying the list of messages. Note that the default ordering of instances can be defined through an OrderBy ViewComponentPart, which the user can override by exploiting the SortAttributes specified in the component.

##### Scrollable list

A very popular behavior in web applications is the paging of long lists of elements into fixed-size blocks, with commands for scrolling. This is often used, for example, as the base of search engine interfaces. A variant is the scrolling of blocks consisting of individual objects, as found, for instance, in image galleries.

**ScrollableList**

The ScrollableList is an extension of the List ViewComponent that allows the user access ordered DataBinding instances grouped in blocks. The ScrollableList ViewComponent has an attribute called “block size” that specifies how many instances constitute a block. It also has an implicit parameter (named current), which holds the block currently in view, and implicit events for moving to the first, last, i-th, next, and previous block.
Figure 7.11 revises the search pattern introduced in chapter 5 to cater to the scrolling of paged results.

##### Nested list

The multilevel master detail pattern illustrated in chapter 5 can be compacted into a ViewComponent, by nesting one list inside another.

**NestedList**

The NestedList is an extension of the List ViewComponent that denotes the nesting of multiple lists, one inside another.
The data model of the NestedList comprises one top-level DataBinding, which typically refers to a class of the domain model. Within the top level DataBinding, one or more first-level NestedDataBindings can be specified that refer to one of the association roles of the class referenced in the top-level DataBinding. Each first-level NestedDataBinding in turn can comprise one or more second-level NestedDataBinding. A second-level NestedDataBinding refers to one of the association roles of the class target of the association role used in the first-level NestedDataBinding. Figure 7.12 shows an example of usage of the NestedList ViewComponent.
The product catalog consists of a three-level nested list. At the top level, categories are displayed. At the next level, the products of each category are listed. At the innermost level, two separate nested lists are presented: the accessories of a product and the other products frequently sold with it. When the user selects a product at the second or third level and an accessory at the third level, the chosen object is displayed either in the “ProductDescription” or in the “AccessoryDescription” ViewContainer.

### Mobile Extensions

Mobile applications have rich interfaces that resemble on a smaller scale those of full-fledged desktop applications. Mobility and the availability of sensors, such as cameras and GPS, introduce features that are best captured by providing extensions of the IFML core specialized for mobile application development.

#### Context Extensions

The context assumes a particular relevance in mobile applications, which must exploit all the available information to deliver the most efficient interface. Therefore, the context must gather all the dimensions that characterize the user intent, the capacity of the access device and of the communication network, and the environment surrounding the user.
Various dimensions of the context relevant to mobile applications have been catalogued and characterized in several standards and standard proposals, briefly overviewed in the bibliographic notes at the end of this chapter. In this section, we exemplify the most interesting ContextDimensions and ContextVariables that characterize mobile application usage. The illustration is not meant to be exhaustive. Rather, its aim is exemplifying how the contextual features can be represented as IFML extensions and used to model the effect of context on the user interface. The main aspects of the Context are listed below. Some of them have to be considered as ContextDimensions (and thus allow the selection of a Context or another), while other are ContextVariables (thus enabling the use of their value as parameters within the IFML models.
- Device: this family of context features can be exploited to specify the adaptation of the interface to different device characteristics, most notably the size and resolution of the screen. These features are usually exploited as ContextDimensions:
  - DiagonalSize: the physical size of the screen, measured as the screen’s diagonal;
  - SizeCategory: for convenience, screen sizes can be grouped in classes that can be treated homogenously (e.g., SMALL, NORMAL, LARGE, EXTRA LARGE); and
  - DensityCategory: for convenience, screen density measures can also be grouped in classes treated homogenously (e.g., LOW, MEDIUM, HIGH, EXTRA HIGH).
The following information becomes handy as ContextVariables, so as to calibrate precisely the UI rendering based on some calculation over the size data:
- PixelSize: the actual horizontal and vertical size of the screen, measured in pixels;
- Density: the quantity of pixels per unit area measured in dpi (dots per inch).
Other characteristics of the device may be considered, such as internal memory size, processing power, and battery status. However, they are less frequently used in the design of applications.
- Network connectivity: this dimension can be used to adapt the quantity or quality of content published in the interface, based on the capacity of the network link (e.g., replacing the display of a large media file with a lighter preview when bandwidth is limited). The relevant ContextDimension is ConnectivityType, which denotes the kind of network available; it can have such values as NONE, BLUETOOTH, NFC, ETHERNET, MOBILE (E, G, 3G, 4G, …), WIFI, and WIMAX;
- Position: this family of features can be used to adapt the interface to the presumed activity of the user (e.g., simplifying the interaction commands when the user is moving) or to publish content that depends on the location (e.g., local news or alerts). The ContextDimensions related to position are:
  - SensorStatus: denotes the activity status of the position engine of the device. It can have values such as: ACTIVE, INACTIVE.
  - Activity: denotes the physical user’s activity inferred by the sensor data; possible values are: still, walking, running, cycling, and in-vehicle.
The ContextVariables that can be exploited when the SensorStatus is ACTIVE are:
- Location: denotes the position of the device, expressed in latitude and longitude coordinates;
- Accuracy: denotes the accuracy of the position.
- Speed: denotes the ground speed of the device.
- Altitude: denotes the altitude above sea level of the device.

#### Containers Extensions

As shown in chapter 4, the composition of mobile application interfaces can be expressed properly with the core IFML concepts of ViewContainers and ViewComponents. However, a characteristic trait of mobile interfaces—also present in desktop applications although less pervasively—is the utilization of predefined ViewContainers devoted to specific functionalities. These system-level containers provide economy of space and enforce a consistent usage of common features. Examples are the “Notifications” area or the “Settings” panel. These special ViewContainers can be distinguished (e.g., by stereotyping them as «system»).

**System ViewContainer**

A ViewContainer stereotyped as «system» denotes a fixed region of the interface, managed by the operating system or by another interface framework in a cross-application way.
Figure 7.13 shows an example of the usage of system ViewContainers by revisiting the e-mail application running example with a simplified composition of the interface more suited to a small screen. A system-level ViewContainers is employed to deliver notifications, which are typically placed in a fixed position within the header region of the interface. Another system ViewContainer, “Settings,” is also used to denote that the standard “Settings” command and window of the operating system are exploited to open the configuration functionality of the e-mail application in the interface region normally devoted to this task for all the applications.
Flexible layouts, another pattern using ViewContainers, are very useful for mobile applications.

#### Component and Event Extensions

Like ViewContainers, ViewComponents can be predefined in the system as default interface elements that provide basic functionality in a consistent manner to the application developer. An example is the media gallery present in most mobile platforms. The «system» stereotype can be applied also to ViewComponents to highlight that the interface uses the components built into the system.

#### Cameras and Sensors

Mobile applications can interact with one or more cameras onboard the device. The basic interaction with the camera requires modeling the ViewContainer for visualizing the camera image and commands, the invocation of an Action for taking the picture, the asynchronous event that notifies that the photo has been taken, and the visualization of the image in the system-level media gallery.
Figure 7.14 shows an example of usage of the camera and of the system-level media gallery. The “PhotoShooter” ViewContainer comprises a system ViewContainer “CameraCanvas,” which denotes the camera image viewer. The “Settings” event opens a modal window for editing the camera parameters, and the “Shoot” event permits the user to take a picture. When the image becomes available, a viewer is activated, from which an event permits the user to open the photo in the system media gallery. The internal viewer is modeled as a scrollable list, with block size = 1 to show one image at a time, and an OrderBy ViewComponentPart with a sorting criterion by timestamp to present the most recent photo first.

#### Communication

Mobile devices communicate in a variety of ways with other fixed or mobile devices that can be discovered dynamically. The aspects of communication that may affect the interface are:
- Connectivity update notifications: they signal the change of the available communication channels and can be captured as system events that express an update of one or more ContextDimensions; and
- Devices in range: other devices can enter or leave the communication range. This feature can be modeled as a system event that signals the discovery of a device. Data transfer activities can be modeled as Actions that encapsulate the details of the protocol used to manage the conversation.
Figure 7.15 shows an example of communication-enabled interface: the usage of near field communication (NFC) for exchanging the contact details of the user.
The application consists of two parts, a sender and a receiver. The “NFCCardSender” interface is minimal, because NFC normally requires the communicating devices to be very close and thus there is little space for user’s interaction. The interface presents the personal data to the user who can confirm his intent to make them available to NFC devices in range. The “SendViaNFC” Action abstracts the steps necessary to build up the NFC record and notify the device that it is ready to be dispatched.
The “NFCCardReceiver” ViewContainer models the application on the side of the receiver. The reception of the NFC payload is modeled as an asynchronous event that abstracts the system process of parsing NFC messages and triggering the registered applications that handle them. The interface is again very basic: the user can confirm and save the data or discard the message.

Figure 7.16 shows an example of adaptation of the interface composition to the network type.
The interface for reading a message is implemented in two versions. One version presents a message with all its attachments downloaded automatically. The second interface requires an explicit user command for downloading an attachment, and the attachments are downloaded and shown one at a time using a ScrollableList. The choice of which alternative interface to use is conditioned by means of an ActivationExpression, illustrated in chapter 5, that tests the type of connectivity available based on the ContextVariable ConnectivityType. On-demand attachment visualization is selected when the connection type is “MOBILE” to reduce bandwidth consumption and interface latency.

#### Position

Location awareness enables devices to establish their position so that mobile applications can provide users with location-specific services and information, set alerts when other devices enter or leave a determined region, and adapt the interface to the current user’s physical activity, such as walking, running, or driving.
Figure 7.17 shows an example of the usage of the position sensor.
The “Start” event in the “Tracker” ViewContainer allows the user to activate the continuous position tracking system of the device. The Form ViewComponent enables the specification of the position tracking parameters, such as accuracy and frequency, which are communicated to the system service via the “ActivatePositionUpdates” Action. After activating the tracking system, the application starts listening to incoming asynchronous SystemEvents, which provide updates of the current position at the established frequency. Such events carry parameters indicating the timestamp of the recording and the geographical coordinates, and trigger a background action that stores such data as “Point” objects. The list of recorded points is visualized in the “TrackingPoints” List ViewComponent. At any moment, the user can clear the list of recordings, save the recorded points as a track object, or stop the position tracking system.

#### Maps

Maps are a powerful interface over geographic data. The integration of digital maps into user interfaces has become very popular with the advent of the web. Mobile applications add a special flavor to map-based interfaces by combining the dynamic position of the user with the representation of topographic data. Digital maps have become a commodity supported by many proprietary and open-source services. This rich offer boosts the development of map-enabled applications on top of off-the-shelf functionality, for:
- connecting to the mapping service and downloading map tiles for display on the device screen with controls such as pan and zoom for moving the map and zooming in or out;
- setting the map type, choosing among several alternatives, such as normal, satellite, hybrid, and 3D; and
- initializing and changing the viewpoint over the map (also called “camera,” to highlight that the map view is modeled as a camera looking down on a flat plane); the rendering of the map is governed by such properties as location, zoom, bearing, and tilt.
A simple way of modeling the map view is to extend the concept of ViewContainer to denote an off-the-shelf map visualization interface. Application-specific content and events can then be added to such an extended ViewContainer as further ViewElements and Events.

**MapView**

A MapView is an extension of ViewContainer that denotes a map view. It supports the events for panning and zooming and for changing the map type and the camera parameters.

Content—both static and interactive—overlaid on the map can be modeled by extending the ViewComponent concept. For example, the «marker» stereotype can be added to Details and List to denote that the DataBinding instances have a position and are rendered on the map as interactive markers.

**Marker**

A Marker is an extension of ViewComponent usable in MapView containers that denotes that the underlying DataBinding instances possess a location attribute that is displayable in a map view. It supports the events for selecting, dragging, and dropping.

Another useful way to present an ordered set of locations is the path visualization.

**Path**

A Path is an extension of the List ViewComponent usable in MapView containers that presents underlying DataBinding instances (that must possess a location attribute) as a polyline in a map view. It supports events for selecting the entire path or a single point on it.
Figure 7.18 elaborates the example of Figure 7.17 to show the usage of the MapView ViewContainer and of the map-specific extensions of the List ViewComponent.
The plain visualization of the tracked points exemplified in Figure 7.17 is replaced by two alternative map-based displays modes. The recorded points are viewable either as a set of markers or as path on the map.

#### Gestures

Touch screens enable the use of gestures for the direct manipulation of screen objects. The gestures supported by touch devices include touch, double touch, press, swipe, fling, drag, pinch in and out, and several more. These gestures have well-defined semantics and consolidated conventions to which the interface design must conform to provide a consistent user experience. They can be represented in IFML by extending the core Event concept.
Figure 7.19 shows an example that uses the touch and press events. The distinction between these two gestures allow a finer control over the effect of acting upon the screen objects, much in the same way as mouse click and double click do in desktop applications.
Figure 7.19 revisits the master detail pattern to highlight the usage of touch gestures. The conventions illustrated in the example adhere to the best practices in popular mobile operating systems, such as Android 4. In a master detail interface, the touch gesture activates the default action on the object (in this case, the opening of the details view). The press gesture instead activates the selection mode, whereby one or more objects can be chosen with a touch event, and a toolbar of commands is displayed to act upon the selected object(s). This behavior is represented in Figure 7.19 by using the «press» and «touch» event extensions and by conditioning the effect of the touch event based on the existence of at least one previously selected object. Other gestural conventions can be represented in a similar way.

### Multiscreen Extensions

Single screen applications are conceived to work for a single class of access devices, with homogeneous capabilities. They define the composition of the interface at design time by specifying the hierarchy of ViewContainers and the disjunctive or conjunctive nesting of containers. Multiscreen applications are instead designed to work on different devices, possibly with different screen characteristics. A goal for their development is to define the interface layout in a flexible way so that it can adapt dynamically to the size, orientation, and density of the screen.
Figure 7.20 shows an application for updating the device settings, designed to adapt to cellular phone small screens and to tablet wider screens. The interface supports two main tasks: picking the desired preference from a list, with the “Preferences” List ViewComponent, and editing its value, with the “PreferenceEditor” Form ViewComponent. The two ViewComponents that address such tasks communicate parameters to the “UpdatePreference” Action through their outgoing NavigationFlows and the ParameterBindingGroups associated with them.
The flexible interface composition is expressed by means of the “Settings” ViewContainer, which hosts two distinct subcontainers: “Tablet Settings,” in which the two ViewComponents are kept together, and “Phone Settings,” in which they are visualized one at a time. The ActivationExpression of the subcontainers ensures that the proper composition pattern is activated based on the device information taken from the Context.
Figure 7.21 shows a mock-up of the interface composition adapted to the type of the screen.
Note that the model of Figure 7.20 duplicates the ViewComponents, Events, InteractionFlows, and Actions that specify the content and behavior of the interface in the two configurations. This duplication, which puts an unnecessary burden on the designer and may result in misalignment errors, can be avoided with the use of modules (explained in chapter 8).

## List of IFML design patterns

The name of a pattern is structured as XY-Z, where:

- X is the category of pattern. For instance, interface organization patterns start with the letter “O,” and content and navigation patterns are prefixed with “CN.”
- Y is the deployment platform where the pattern originated or is most frequently found. For instance, desktop patterns are labeled with “D,” web with “W,” mobile with “M.” The prefix is omitted for patterns that apply equally well to multiple platforms and for which there is no clearly prevalent platform.
- Z is a mnemonic label identifying the specific pattern.

### Interface Organization Patterns
| Code    | Title                                        | Description                                                                                                                                      |
| ------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| OD-SWA  | Simple work area                             | Distinguishes a work area where the main tasks of the application are performed along with one or more service areas                             |
| OD-MWA  | Multiview work area                          | Extension of OD-SWA for multiple alternative views of the item in the work area                                                                  |
| OD-CWA  | Composite work area                          | Splits the work area into subregions devoted to different perspectives of the item, presented simultaneously                                     |
| OD-MCWA | Multiview composite work area                | Combines the decomposition of the work area into alternative perspectives and simultaneous partial views                                         |
| OW-MFE  | Multiple front ends on the same domain model | Provides different interfaces for different user roles upon the same information                                                                 |
| OW-LWSA | Large web sites organized into areas         | Applications that exhibit a hierarchical structure, whereby the pages of the site are clustered into sections dealing with a homogeneous subject |
| OM-MSL  | Mobile screen layout                         | Maps the interface to a top-level grid that contains three regions: the header, the content area, and the footer                                 |

### Content and Navigation Patterns
| Code             | Title                                       | Description                                                                                                                                                                                                                                                                     |
| ---------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CN-MD and CN-MMD | Master detail and Master multidetail        | Presents some items, and a selection permits the user to access the details of one instance at a time                                                                                                                                                                           |
| CN-MLMD          | Multilevel master detail                    | Also called a cascaded index; consists of a sequence of lists over distinct classes, such that each list specifies a change of focus from one object, selected from the index to the set of objects related to it via an association role; in the end, a single object is shown |
| CN-DEF           | Default selection                           | Simulates a user choice at the initial access of a list, thus selecting a default instance                                                                                                                                                                                      |
| CN-SOT           | Single object toolbar                       | Content-dependent toolbar that supports commands upon one object                                                                                                                                                                                                                |
| CN-MOT           | Multiple object toolbar                     | Content-dependent toolbar with commands that can be applied to multiple objects                                                                                                                                                                                                 |
| CN-DT            | Dynamic toolbar                             | Toolbar with commands that may vary at runtime based on the status of the interaction                                                                                                                                                                                           |
| CN-MSC           | Multistep commands                          | Commands that involve multiple interaction steps                                                                                                                                                                                                                                |
| CN-CII           | Commands with inline input                  | Collapses in the toolbar several steps needed to perform an action                                                                                                                                                                                                              |
| CN-CIM&B         | Content-independent navigation bar and menu | Groups commands that do not act upon specific objects but shortcut the navigation or help the user go back quickly                                                                                                                                                              |
| CN-UP            | Up navigation                               | Refers to some hierarchical structure associated with the interface; it leads the user to the superior element in the view hierarchy                                                                                                                                            |
| CN-BACK          | Back navigation                             | “Back” refers to the chronology of user interaction; it leads back to the last visited ViewElement                                                                                                                                                                              |
| CN-BREAD         | Breadcrumbs                                 | A navigation aid that shows the user location in the application interface                                                                                                                                                                                                      |
| CN-PG            | Paging                                      | Displays a block of objects at a time and allows the user to scroll rapidly through the collection                                                                                                                                                                              |
| CN-PR            | Collection preview                          | Used with CN-PG, provides a preview of the object’s location in the sequence and of what comes before and after                                                                                                                                                                 |
| CN-ALPHA         | Alphabetical filter                         | Provides an alphabetic filter to partition the collection into chunks                                                                                                                                                                                                           |

### Data Entry Patterns
| Code    | Title                           | Description                                                                                                          |
| ------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| DE-FRM  | Multifield forms                | Form for submitting information through several fields                                                               |
| DE-PLDF | Preloaded field                 | Variant of DE-FRM where some fields are preloaded with an existing value                                             |
| DE-PASF | Pre-assigned selection field    | Form where the value of a selection field is preselected                                                             |
| DE-DLKP | Data lookup                     | Data entry task that involves looking up information for filling in the fields                                       |
| DE-CSF  | Cascade selection fields        | The data entry task involves entering a set of selections that have some kind of dependency on one another           |
| DE-WIZ  | Wizard                          | Partition of a data entry procedure into logical steps that must be followed in a determined sequence                |
| DE-TDFP | Type-dependent field properties | Provides data entry facilities for form fields of specific data types                                                |
| DE-RTE  | Rich text editing               | Provides an enriched text field in the shape of a microapplication that embodies the commands applicable to the text |
| DE-AUTO | Input auto-completion           | Automatically provides suggestions for completing the input based on what the user has already typed in a field      |
| DE-DYN  | Dynamic selection fields        | Occurs when the application requires the user to input data that have dependencies                                   |
| DE-INPL | In-place editing                | Allows the user to edit content without abandoning the current view to access a data entry form                      |
| DE-VAL  | User input validation           | Checks the correctness of the user input against validation rules and returns appropriate notification message(s)    |

### Content Search Patterns
| Code    | Title                 | Description                                                                                                                                                                               |
| ------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CS-SRC  | Basic search          | Keyword search upon a collection of items                                                                                                                                                 |
| CS-MCS  | Multicriteria search  | Composite search criteria upon a collection of items                                                                                                                                      |
| CS-FSR  | Faceted search        | Allows the progressive refinement of search results upon structured multidimensional data, by restricting the objects that match the query based on their property values                 |
| CS-RSRC | Restricted search     | Restricts the search focus to specific subcollections when searching large collections                                                                                                    |
| CS-SRCS | Search suggestions    | Exploits the auto-completion pattern and requires the logging of keywords previously inserted by the users; logged keywords matching the current user input are shown sorted by frequency |
| GEO-LAS | Location-aware search | Enables search of items that are related and close to the current user position                                                                                                           |

### Content Management Patterns
| Code     | Title                           | Description                                                                                                                                  |
| -------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| CM-OCR   | Object creation                 | Enables the creation of a new object in a data storage                                                                                       |
| CM-OACR  | Object and association creation | Creates a new object and sets its associations to other objects                                                                              |
| CM-ODL   | Object deletion                 | Deletes one or more objects of a given class                                                                                                 |
| CM-CODL  | Cascaded deletion               | Removes a specific object and all the objects associated with it via one or more associations                                                |
| CM-OM    | Object modification             | Updates one or more objects of a given class                                                                                                 |
| CM-AM    | Association management          | Used to create, replace, or delete instances of an association, by connecting or disconnecting some objects of the source and target classes |
| CM-NOTIF | Notification                    | The interface is updated (typically asynchronously) by the occurrence of a system generated event                                            |
| CM-CBCM  | Class-based content management  | Addresses the creation, modification and deletion of an object and its association instances                                                 |
| CM-PBCM  | Page-based content management   | Supports blogs and page-based content management systems; management of whole pages is allowed                                               |

### Identification and Authorization Patterns
| Code               | Title                                               | Description                                                                                                                |
| ------------------ | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| IA-LOGIN           | Login                                               | Recognizes and checks the validity of a user-provided identity                                                             |
| IA-LOGOUT          | Logout                                              | Clears user’s authenticated identity preserved in the application navigation context upon explicit user request            |
| IA-CEX             | Context expiration notification                     | The authenticated identity of the user is cleared by the system for security reasons or because of timeout                 |
| IA-SPLOG           | Login to a specific ViewContainer                   | Recognizes and checks the validity of a user-provided identity and enables access to a specific part of the user interface |
| IA-ROLE            | User role display and switching                     | Displays the user role and allows change of role                                                                           |
| IA-RBP and IA-NRBP | (Negative) role-based permissions for view elements | Implements (possibly negative) access permissions at the view level that depend on the user’s role                         |
| IA-OBP             | Object-based permissions                            | Access control is expressed over the content objects and personalization associations in the content model                 |
| IA-PRO             | User profile display and management                 | Shows and enables the editing of application-dependent information associated with the identity of an authenticated user   |
| IA-IPSI            | In-place sign-in                                    | When the user attempts to trigger an action, the user is warned of the need to sign in and then routed to the login form   |

### Session Management Patterns
| Code    | Title                                      | Description                                                                                                                             |
| ------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| SES-CR  | Creating session data from persistent data | Stores information in the navigation session by collecting them from a persistent data source                                           |
| SES-PER | Persisting session data                    | Creates persistent data from user navigation session data                                                                               |
| SES-EXC | Session data expiration catching           | Handles the asynchronous notification of the expiry of the session to the user interface by causing an automatic refresh of the content |

### Social Functions Patterns
| Code   | Title                           | Description                                                                                  |
| ------ | ------------------------------- | -------------------------------------------------------------------------------------------- |
| SOC-AW | Activity wall                   | Logs the social activity typical of a social network platform                                |
| SOC-SH | Sharing, liking, and commenting | Enables posting, commenting, liking, and sharing content produced by other community members |
| SOC-FR | Friendship management           | Manages a symmetric (friendship) or asymmetric (following) association between users         |