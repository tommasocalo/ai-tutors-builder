var TUTOR_ID = null;
var LOG = [];
/**
 * This script initializes event handlers and other initial setup requirements once the DOM is fully loaded.
 * It ensures that the DOM elements are available before any JavaScript operations are attempted on them.
 */
$(document).ready(function (e) {
  let isSaved = 0;
  let trainID = 0;
  let item_count = 0;


  function buildHTMLFromCompactRepresentationND(compactRep, componentName) {

    // Function to create an HTML string for an element with optional class, placeholder, and additional attributes
    function createElement(tag, className, placeholder, dataType, content = "") {
      let attributes = "";
      if (className) attributes += ` class="${className}"`;
      if (placeholder) attributes += ` placeholder="${placeholder}" readonly`;
      if (dataType) {
        if (componentName) {
          attributes += ` data-type="${dataType}"  type="button" id="galleryItem_${componentName}_${item_count++}"`;
        } else {
          attributes += ` data-type="${dataType}"  type="button" id="newItem_${item_count++}"`;
        }
      }
      if (tag === "input") {
        attributes += ` style="border: none;box-shadow: none;text-align: center;"`;
      }
      return `<${tag}${attributes}>${content}</${tag}>`;
    }

    // Function to recursively process and generate HTML string from the compact representation
    function appendElementsFromCompactRep(compactString, isChild = false) {
      const regex = /(\w+)\[([^\]]+)\]|\w+\s*{/g;
      let match,
        html = "";

      while ((match = regex.exec(compactString)) !== null) {
        const [matchedString, type, content] = match;
        if (type && content) {
          switch (type) {
            case "title":
            case "label":
              const divClass =
                type === "title"
                  ? "btn-primary btn-tutor-title"
                  : "btn-success btn-label row";
              const dt =
                type === "title"
                  ? "page-items"
                  : "page-row";
              const p = createElement("p", "page-item", null, null, content) + createElement("p", "removeFromDom", null, null, "Tutor Title")
              const q = createElement("p", "page-item align-self-center", null, null, content) + createElement("p", "removeFromDom", null, null, "Label")
              const f = type === "title" ? p : q;
              html += createElement(
                "div",
                `btn ${divClass} rounded-button`,
                null,
                dt,
                f
              );
              break;
            case "input":
              const input = createElement("input", "form-control", content, null);
              input.style = "border: none;box-shadow: none;text-align: center;";
              html += createElement(
                "div",
                "btn btn-light btn-input-box-t rounded-button",
                null,
                "page-row",
                input
              );
              break;
          }
        } else if (matchedString.trim().endsWith("{")) {
          const elementType = matchedString.trim().replace("{", "").trim();
          const divType = elementType === "row" ? "page-row" : "page-items";
          const divClass =
            elementType === "row"
              ? "btn-warning btn-row btn-row-item grid"
              : "btn-info btn-column";
          const pRemove = createElement(
            "p",
            "removeFromDom",
            null,
            null,
            elementType.charAt(0).toUpperCase() + elementType.slice(1)
          );
          const ulClass =
            elementType === "row"
              ? "list one page-item-ul grid grid-flow-col gap-1"
              : "list one d-flex flex-column gap-2 page-item-rl-row";
          const ulId =
            elementType === "row" ? "page-item-ul" : "page-item-rl-row";
          const closeIndex = findClosingIndex(compactString, regex.lastIndex);
          const innerContent = compactString.substring(
            regex.lastIndex,
            closeIndex
          );
          const ulContent = appendElementsFromCompactRep(innerContent, true);
          const ul = `<ul class="${ulClass}" data-type="page-row">${ulContent}</ul>`;

          html += createElement(
            "div",
            `btn ${divClass} drop-box rounded-button`,
            null,
            divType,
            pRemove + ul
          );
          regex.lastIndex = closeIndex + 1;
        }
      }
      if (isChild) {
        return html;
      } else {
        const pageDiv = createElement("div", null, null, "page-items", html);
        const finalContainerDiv = createElement(
          "div",
          "container mx-auto flex flex-col py-1 justify-center items-center",
          null,
          null,
          ""
        );
        return html + finalContainerDiv;
      }
    }

    function findClosingIndex(str, openIndex) {
      let stack = 1;
      for (let i = openIndex; i < str.length; i++) {
        if (str[i] === "{") stack++;
        else if (str[i] === "}") stack--;

        if (stack === 0) return i;
      }
      return -1; // Handle malformed strings gracefully
    }
    html = appendElementsFromCompactRep(compactRep)
    return html;
  }

  function buildHTMLFromCompactRepresentation(compactRep, componentName) {

    // Function to create an HTML string for an element with optional class, placeholder, and additional attributes
    function createElement(tag, className, placeholder, dataType, content = "") {
      let attributes = "";
      if (className) attributes += ` class="${className}"`;
      if (placeholder) attributes += ` placeholder="${placeholder}" readonly`;
      if (dataType) {
        if (componentName) {
          attributes += ` data-type="${dataType}" draggable="true" type="button" id="galleryItem_${componentName}_${item_count++}"`;
        } else {
          attributes += ` data-type="${dataType}" draggable="true" type="button" id="newItem_${item_count++}"`;
        }
      }
      if (tag === "input") {
        attributes += ` style="border: none;box-shadow: none;text-align: center;"`;
      }
      return `<${tag}${attributes}>${content}</${tag}>`;
    }

    // Function to recursively process and generate HTML string from the compact representation
    function appendElementsFromCompactRep(compactString, isChild = false) {
      const regex = /(\w+)\[([^\]]+)\]|\w+\s*{/g;
      let match,
        html = "";

      while ((match = regex.exec(compactString)) !== null) {
        const [matchedString, type, content] = match;
        if (type && content) {
          switch (type) {
            case "title":
            case "label":
              const divClass =
                type === "title"
                  ? "btn-primary btn-tutor-title"
                  : "btn-success btn-label row";
              const dt =
                type === "title"
                  ? "page-items"
                  : "page-row";
              const p = createElement("p", "page-item", null, null, content) + createElement("p", "removeFromDom", null, null, "Tutor Title")
              const q = createElement("p", "page-item align-self-center", null, null, content) + createElement("p", "removeFromDom", null, null, "Label")
              const f = type === "title" ? p : q;
              html += createElement(
                "div",
                `btn ${divClass} rounded-button`,
                null,
                dt,
                f
              );
              break;
            case "input":
              const input = createElement("input", "form-control", content, null);
              input.style = "border: none;box-shadow: none;text-align: center;";
              html += createElement(
                "div",
                "btn btn-light btn-input-box-t rounded-button",
                null,
                "page-row",
                input
              );
              break;
          }
        } else if (matchedString.trim().endsWith("{")) {
          const elementType = matchedString.trim().replace("{", "").trim();
          const divType = elementType === "row" ? "page-row" : "page-items";
          const divClass =
            elementType === "row"
              ? "btn-warning btn-row btn-row-item grid"
              : "btn-info btn-column";
          const pRemove = createElement(
            "p",
            "removeFromDom",
            null,
            null,
            elementType.charAt(0).toUpperCase() + elementType.slice(1)
          );
          const ulClass =
            elementType === "row"
              ? "list one page-item-ul grid grid-flow-col gap-1"
              : "list one d-flex flex-column gap-2 page-item-rl-row";
          const ulId =
            elementType === "row" ? "page-item-ul" : "page-item-rl-row";
          const closeIndex = findClosingIndex(compactString, regex.lastIndex);
          const innerContent = compactString.substring(
            regex.lastIndex,
            closeIndex
          );
          const ulContent = appendElementsFromCompactRep(innerContent, true);
          const ul = `<ul class="${ulClass}" data-type="page-row">${ulContent}</ul>`;

          html += createElement(
            "div",
            `btn ${divClass} drop-box rounded-button`,
            null,
            divType,
            pRemove + ul
          );
          regex.lastIndex = closeIndex + 1;
        }
      }
      if (isChild) {
        return html;
      } else {
        const pageDiv = createElement("div", null, null, "page-items", html);
        const finalContainerDiv = createElement(
          "div",
          "container mx-auto flex flex-col py-1 justify-center items-center",
          null,
          null,
          ""
        );
        return html + finalContainerDiv;
      }
    }

    function findClosingIndex(str, openIndex) {
      let stack = 1;
      for (let i = openIndex; i < str.length; i++) {
        if (str[i] === "{") stack++;
        else if (str[i] === "}") stack--;

        if (stack === 0) return i;
      }
      return -1; // Handle malformed strings gracefully
    }
    html = appendElementsFromCompactRep(compactRep)
    return html;
  }
  /**
   * Initializes click event on the generate button.
   * Shows a loading spinner, captures the content of the textarea, and makes an AJAX POST request to generate a tutor layout.
   * On success, it converts the compact layout response to HTML and appends it to the page.
   * On error, it displays an alert message and hides the loading spinner.
   */
  $("#generate_btn").click(function () {
    $("#loadingSpinner").show();

    const textareaContent = $(".tutor-designer-input").val();
    // AJAX request to server to generate tutor layout
    $.ajax({
      url: "/generateTutorLayout", // Endpoint to generate layout
      type: "POST",
      data: JSON.stringify({ text: textareaContent }),
      contentType: "application/json",
      success: function (response) {
        // Use the response to display the generated tutor layout
        const compactLayout = response.compactLayout;
        // Assuming function to convert compact layout to HTML and append it to the page
        $("#page-container").html(
          buildHTMLFromCompactRepresentation(compactLayout, false)
        );
        // // Find the first .btn-column in the page
        // let btnColumn = $('.btn-column').first();

        // // Find the closest child of btnColumn with the class .list.one.d-flex.flex-column.gap-2
        // let listContainer = btnColumn.find('.list.one.d-flex.flex-column.gap-2').first();
        // var listcont = $('#page-item-rl-row').first();

        // if (listContainer.length > 0 && btnColumn.length > 0) {
        //     // Calculate the height of listContainer
        //     let contentHeight = listContainer[0].scrollHeight;
        //     // Set the height of the btnColumn based on the contentHeight + 100px for extra space
        //     btnColumn.css('height', `${contentHeight + 100}px`);
        //     listcont.css('height', `${contentHeight + 100}px`)
        // }

        $("#loadingSpinner").hide();
      },
      error: function (error) {
        console.error("Error generating tutor layout:", error);
        alert("Failed to generate tutor layout, ensure valid OpenAI key.");
        $("#loadingSpinner").hide();
      },
    });
  });
  /**
   * Initializes click event on generate component buttons.
   * Shows a spinner overlay, captures the component name and input content, and makes an AJAX POST request to generate a component layout.
   * On success, it converts the compact layout response to HTML for the specific component.
   * On error, it displays an alert message and hides the spinner overlay.
   */
  $(document).on("click", ".generate_component_btn", function () {
    const $thisButton = $(this); // Capture the button that was clicked

    $thisButton.closest(".component-item").find(".spinner-overlay").show();
    const componentName = $thisButton
      .closest(".component-item")
      .find(".component-name")
      .text()
      .trim();
    const textareaContent = $thisButton
      .closest(".input-group")
      .find(".form-control")
      .val();
    // AJAX request to server to generate tutor layout
    $.ajax({
      url: "/generateComponentLayout", // Endpoint to generate layout
      type: "POST",
      data: JSON.stringify({ text: textareaContent }),
      contentType: "application/json",
      success: function (response) {
        // Use the response to display the generated tutor layout
        const compactLayout = response.compactLayout;
        // Find the component-details-content list related to the clicked button
        const $componentDetailsContent = $thisButton
          .closest(".component-item")
          .find(".component-details-content");
        // Assuming function to convert compact layout to HTML
        $componentDetailsContent.html(
          buildHTMLFromCompactRepresentation(compactLayout, componentName)
        );
        $thisButton.closest(".component-item").find(".spinner-overlay").hide();
      },
      error: function (error) {
        console.error("Error generating component layout:", error);
        alert("Failed to generate component layout, ensure valid OpenAI key.");
        $thisButton.closest(".component-item").find(".spinner-overlay").hide();
      },
    });
  });
  /**
   * Handles click events on elements with the 'closeModal' class.
   * This function hides three specific modals: '#alertModal', '#SuccessModal', and '#TrainModal'.
   * It's designed to be attached to any closeModal button or link within the application.
   * The page reload line is commented out, but can be enabled if a fresh state is required after modal closure.
   */
  $(".closeModal").click(function () {
    $("#alertModal").modal("hide");
    $("#SuccessModal").modal("hide");
    $("#TrainModal").modal("hide");
    //  window.location.reload()
  });
  /**
   * Attaches a click event handler to elements with the 'closeModal_not_reload' class.
   * When such an element is clicked, it hides the '#alertModal' and '#SuccessModal',
   * then smoothly scrolls the page back to the top.
   * This function is useful for closing modals without refreshing the page and ensuring
   * the user is returned to the start of the document, improving the UX after modal closure.
   */
  $(".closeModal_not_reload").click(function () {
    $("#alertModal").modal("hide");
    $("#SuccessModal").modal("hide");
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });
  /**
   * Attaches a click event handler to the '#mytutor_rename' button.
   * This function retrieves the ID of the tutor from the first cell of the parent table row and
   * the new name of the tutor from the '#tutor_rename' input field. It then creates a log item
   * for this action and prepares the data for the POST request to the server's "/rename" endpoint.
   * Upon success, it displays a success modal to the user. Errors during the AJAX call are not
   * explicitly handled beyond default browser logging.
   */
  $("#mytutor_rename").click(function () {
    var deleteButton = $(this).parents("tr").find(".btn.btn-dark.black_color[data-modal-target='popup-modal']");

    Id = deleteButton.data('id');

    tutorName = $("#tutor_rename").val();
    var log_item = create_log_item(
      "Tutor Building",
      "Tutor",
      Id,
      "Tutor Rename",
      tutorName
    );
    var data = get_request_body(Id, tutorName, null, log_item);

    $.ajax({
      url: "/rename",
      // dataType: 'json',
      data: JSON.stringify(data),
      type: "POST",
      contentType: "application/json",
      success: function (response) {
        $("#SuccessModal").modal("show");
      },
      error: function (error) {
        //console.log(error);
      },
    });
  });
  /**
   * Attaches a click event listener to the button with the ID `btn_update_tutor`.
   * When triggered, it performs the following actions:
   * 1. Retrieves the current HTML content of the element with the ID `page`.
   * 2. Captures the text of the first paragraph element within an element having both `btn-tutor-title` and `page-item` classes, assumed to be the tutor's name.
   * 3. Constructs an object containing both the retrieved content and tutor name.
   * 4. Sends this object as a JSON string in a POST request to the server endpoint `/update_tutor_content`.
   *    - On successful request completion, it displays the `#SuccessModal` to indicate the update was successful.
   *    - If the request fails, the error handling is currently minimal and may be expanded as needed.
   *
   * This implementation assumes that the server endpoint correctly handles the data to update the tutor content.
   */
  $("#btn_update_tutor").click(function () {
    var content = $("#page").html();

    var tutorName = $(".btn-tutor-title p.page-item").text();

    var content = {
      content: content,
      tutorName: tutorName,
    };

    $.ajax({
      url: "/update_tutor_content",
      data: JSON.stringify(content),
      type: "POST",
      contentType: "application/json",
      success: function (response) {
        //console.log("response", JSON.stringify(content));
        $("#SuccessModal").modal("show");
      },
      error: function (error) {
        //console.log(error);
      },
    });
  });
  /**
   * Attaches a click event listener to elements with the class `mytutor_upload`.
   * Upon clicking, the listener performs the following operations:
   * 1. Retrieves the ID of the tutor from the first table cell (`<td>`) of the parent row (`<tr>`). This ID uniquely identifies the tutor.
   * 2. Constructs an object with `IsOnline` set to `1` and `id` set to the retrieved tutor ID. This object signifies the intent to update the tutor's online status to true.
   * 3. Sends this object as JSON in a POST request to the `/update_tutor_online` server endpoint.
   *    - If the request is successful, it shows the `#SuccessModal`, signaling the update was successful.
   *    - In case of an error, the handling is minimal, but could be extended to provide more feedback.
   *
   * This mechanism allows for the dynamic updating of a tutor's online status without requiring a page reload.
   */

  $(".mytutor_upload").click(function () {
    var deleteButton = $(this).parents("tr").find(".btn.btn-dark.black_color[data-modal-target='popup-modal']");

    Id = deleteButton.data('id');

    var content = {
      IsOnline: 1,
      id: Id,
    };

    $.ajax({
      url: "/update_tutor_online",
      data: JSON.stringify(content),
      type: "POST",
      contentType: "application/json",
      success: function (response) {
        //console.log("response", JSON.stringify(content));
        $("#SuccessModal").modal("show");
      },
      error: function (error) {
        //console.log(error);
      },
    });
  });

  /**
   * Attaches a click event listener to the element with the ID `mytutor_delete`.
   * This function facilitates the deletion of a tutor's record from the server:
   * 1. Determines the tutor's unique ID by extracting the content of the first table cell (`<td>`) in the closest row (`<tr>`) to the clicked button. This ID is critical for identifying which tutor record to delete.
   * 2. Forms an object with the tutor's ID, preparing it for transmission to the server.
   * 3. Executes a POST request to the `/delete` endpoint, sending the tutor's ID as a JSON string.
   *    - On successful deletion (as indicated by the server's response), it displays the `#SuccessModal`, notifying the user of the successful operation.
   *    - In case of an error during the request (e.g., server-side issues, network problems), the current setup does not explicitly handle such errors, but developers could implement error handling mechanisms to enhance user feedback and experience.
   *
   * This method allows for the dynamic removal of tutor records without the need to reload the webpage, streamlining the user experience in managing tutor information.
   */
  $("#mytutor_delete").click(function (event) {

    var deleteButton = $(this).closest("tr").find(".btn.btn-dark.black_color[data-modal-target='popup-modal']");
    // Retrieve the 'data-id' from the found "Delete" button
    var Id = deleteButton.data('id');

    var data = {
      Id: Id,
    };

    $.ajax({
      url: "/delete",
      // dataType: 'json',
      data: JSON.stringify(data),
      type: "POST",
      contentType: "application/json",
      success: function (response) {
        $("#SuccessModal").modal("show");
        $('tr[data-id="' + Id + '"]').remove(); // Remove the row with the matching data-id attribute

      },
      error: function (error) {
        //console.log(error);
      },
    });
  });

  allNames = [];
  selectedElements = [];

  var count = 0;
  /**
   * Attaches a click event listener to the element with the ID `tutor_reset`.
   * Upon clicking, this function performs a simple operation:
   * 1. It changes the current location of the browser to the `/tutor_builder` URL, effectively redirecting the user to the tutor builder page.
   * 
   * This approach is used to reset the current state or data in the tutor builder interface by navigating the user away from the current page and then back to the tutor builder page, providing a fresh start without requiring manual page refreshes or data clearing by the user.
   */
  $("#tutor_reset").click(function () {
    $(location).attr("href", "/tutor_builder");
  });
  /**
   * Attaches a click event listener to elements with the class `mytutor_edit`.
   * This function is designed to facilitate the editing of a tutor's information:
   * 1. Retrieves the unique ID of the tutor from the first table cell (`<td>`) within the same row (`<tr>`) as the clicked button. This ID is essential for identifying which tutor record to edit.
   * 2. Packages this ID into an object for transmission.
   * 3. Initiates a POST request to the `/tutor_edit` endpoint with the tutor's ID as a JSON payload.
   *    - On successful response, the browser is redirected to the `/edit` page, intended for editing tutor information. Additionally, the response presumed to contain the tutor's editable data (`response.tutor`) is stored in the browser's local storage under the key `content` and the page content is replaced with the received data.
   *    - If the request fails, error handling is not explicitly detailed here, but could involve displaying a message to the user or logging the error for debugging purposes.
   *
   * Note: This function assumes the server responds with a JSON object containing the tutor's data necessary for editing. The operation to replace the page content (`$("#page").replaceWith(result);`) suggests an immediate display of the tutor's information for editing, although this action seems redundant given the preceding redirection to `/edit`.
   */
  $(".mytutor_edit").click(function () {
    var deleteButton = $(this).parents("tr").find(".btn.btn-dark.black_color[data-modal-target='popup-modal']");

    Id = deleteButton.data('id');

    var data = {
      Id: Id,
    };

    $.ajax({
      url: "/tutor_edit",
      dataType: "json",
      data: JSON.stringify(data),
      type: "POST",
      contentType: "application/json",
      success: function (response) {
        window.location.href = "/edit";

        var result = response.tutor;

        localStorage.setItem("content", result);

        //console.log( $('#page').html())
        $("#page").replaceWith(result);
      },
      error: function (error) {
        //console.log(error);
      },
    });
  });
  /**
   * Attaches a click event listener to elements with the class `mytutor_preview`.
   * This listener is responsible for fetching a preview of a specific tutor's content based on their ID:
   * 1. Retrieves the tutor's ID by finding the first table cell (`<td>`) content in the same row (`<tr>`) as the clicked button. The ID is essential for identifying which tutor's preview to fetch.
   * 2. Packages the tutor's ID into an object to be sent to the server.
   * 3. Initiates a POST request to the `/tutor_preview` endpoint with the tutor's ID as the payload.
   *    - If the request is successful, the browser is redirected to the `/preview` URL to show the fetched tutor's content.
   *    - As part of the success callback, the tutor's content received from the server (assumed to be in the `response.tutor`) is stored in `localStorage` under the key `content`. This stored content could be used in the preview page to display the tutor's information.
   *    - Additionally, the current content of the element with the ID `page` is replaced with the fetched tutor's content, allowing for immediate preview if the redirection does not happen for some reason.
   *    - In case of an error during the AJAX request, the error handling is currently minimal but could be enhanced to provide feedback to the user.
   *
   * This mechanism enables dynamic previewing of tutor content without the need for page reloads, offering a more seamless user experience.
   */
  $(".mytutor_preview").click(function () {
    var deleteButton = $(this).parents("tr").find(".btn.btn-dark.black_color[data-modal-target='popup-modal']");

    Id = deleteButton.data('id');

    var data = {
      Id: Id,
    };

    $.ajax({
      url: "/tutor_preview",
      dataType: "json",
      data: JSON.stringify(data),
      type: "POST",
      contentType: "application/json",
      success: function (response) {
        window.location.href = "/preview";

        var result = response.tutor;

        localStorage.setItem("content", result);

        //console.log( $('#page').html())
        $("#page").replaceWith(result);
      },
      error: function (error) {
        //console.log(error);
      },
    });
  });
  /**
   * Attaches a click event listener to elements with the class `mytutor_train`.
   * This function initiates a training process for a specific tutor by performing the following steps:
   * 1. Retrieves the ID of the tutor from the first table cell (`<td>`) within the same row (`<tr>`) as the clicked element. This ID uniquely identifies the tutor for which the training is to be initiated.
   * 2. Forms a data object containing the tutor's ID, which is sent to the server to specify which tutor is to undergo training.
   * 3. Sends an AJAX POST request to the `/tutor_train` endpoint, passing the tutor's ID as JSON.
   *    - Upon successful completion of the request, the function redirects the browser to the `/train` URL. This page is intended to show the status or result of the training process.
   *    - The response from the server is expected to include the trained tutor's content (`response.tutor`) and a unique identifier for the tutor (`response.tutor_id`). Both pieces of information are stored in `localStorage` for use on the training status/result page.
   *    - The content of the element with the ID `page` is replaced with the tutor's content provided in the response, allowing the user to see an immediate preview or result of the training if needed.
   *    - If the request fails due to server error or network issues, the error handling currently does not provide specific feedback but could be implemented to alert the user to the issue.
   *
   * This interactive functionality enhances the user experience by enabling on-the-fly training of tutors without the need for manual page refreshes or navigation.
   */
  $(".mytutor_train").click(function () {
    //console.log("This is train function!!!!!");

    Id = $(this).parents("tr").find("td").eq(0).html();

    var data = {
      Id: Id,
    };

    $.ajax({
      url: "/tutor_train",
      dataType: "json",
      data: JSON.stringify(data),
      type: "POST",
      contentType: "application/json",
      success: function (response) {
        window.location.href = "/train";

        localStorage.setItem("content", response.tutor);
        localStorage.setItem("tutor_id", response.tutor_id);

        //console.log( $('#page').html())
        $("#page").replaceWith(response.tutor);
      },
      error: function (error) {
        //console.log(error);
      },
    });
  });
  /**
   * Saves the current tutor's information to the server. It captures the tutor's ID, content from a specified container, 
   * and the tutor's name from a specific location within the document. It constructs a data object to send to the server,
   * including handling cases where the tutor's name might be empty or might already exist in the `tutorNames` array.
   * 
   * If the tutor's name is empty, an alert modal is shown. If the tutor's name is unique (not found in the `tutorNames` array),
   * it proceeds to save the tutor's information via a POST request. If the name already exists within the array, a modal
   * indicating a duplicate name is shown. Upon successful save, a success modal is displayed, the global log is cleared, 
   * a saved flag is set, and the ID returned from the server is stored.
   * 
   * This function assumes the presence of global variables or elements like `LOG`, `isSaved`, `trainID`, and `tutorNames`,
   * as well as the function `get_request_body` for constructing the request payload.
   */
  function save_tutor() {
    console.log("OK")
    //Id = $(this).parents("tr").find("td").eq(0).html();
    var deleteButton = $(this).parents("tr").find(".btn.btn-dark.black_color[data-modal-target='popup-modal']");
    // Retrieve the 'data-id' from the found "Delete" button
    Id = deleteButton.data('id');

    var content = $("#page_parent").html();
    var tutorName = $(".btn-tutor-title p.page-item").text();

    var data = get_request_body(null, tutorName, content, LOG);
    console.log(data);

    if (tutorName.trim() === "") {
      $("#alertModal").modal("show");
    } else {
      if (tutorNames.length === 0) {
        $.ajax({
          url: "/save",
          // dataType: 'json',
          data: JSON.stringify(data),
          type: "POST",
          contentType: "application/json",
          success: function (response) {
            //console.log("response", JSON.stringify(data));
            $("#SuccessModal").modal("show");
            LOG = [];
            isSaved = 1;
            //console.log(response.id);
            trainID = response.id;
          },
          error: function (error) {
            //console.log(error);
          },
        });
      } else {
        for (var j = 0; j < tutorNames.length; j++) {
          if (tutorNames[j] === tutorName) {
            $("#exampleModal").modal("show");
            break;
          } else if (
            j === tutorNames.length - 1 &&
            tutorNames[tutorNames.length - 1] !== tutorName
          ) {
            $.ajax({
              url: "/save",
              // dataType: 'json',
              data: JSON.stringify(data),
              type: "POST",
              contentType: "application/json",
              success: function (response) {
                //console.log("response", JSON.stringify(data));
                $("#SuccessModal").modal("show");
                LOG = [];
                //console.log(response.id);
                isSaved = 1;
                trainID = response.id;
              },
              error: function (error) {
                //console.log(error);
              },
            });
          }
        }
      }
    }
  }

  $("#btn_save_tutor").click(function () {
    Id = $(this).parents("tr").find("td").eq(0).html();
    var content = $("#page_parent").html();
    var tutorName = $(".btn-tutor-title p.page-item").text();

    var data = get_request_body(null, tutorName, content, LOG);
    console.log(data);

    $.ajax({
      url: "/save",
      // dataType: 'json',
      data: JSON.stringify(data),
      type: "POST",
      contentType: "application/json",
      success: function (response) {
        //console.log("response", JSON.stringify(data));
        $("#SuccessModal").modal("show");
        LOG = [];
        // $(location).attr('href','/tutor_builder');
      },
      error: function (error) {
        //console.log(error);
      },
    });

    // window.location.reload();
  });
  /**
   * Checks if the "page-container" element is empty or not.
   * Specifically, it looks for the presence of any `<div>` elements within "page-container".
   * @returns {boolean} True if "page-container" does not contain any `<div>` elements, indicating it is empty. Otherwise, false.
   */
  function isEmptyTutor() {
    inner = document.getElementById("page-container");
    //console.log(inner.innerHTML);
    if (!inner.innerHTML.includes("div")) {
      return true;
    } else {
      return false;
    }
  }

  $("#btn_myTutors").click(function () {
    if (isEmptyTutor()) {
      $("#confirmModal").data("page", "/my_tutors");
      window.location.href = $("#confirmModal").data("page");
    } else {
      if (isSaved == 0) {
        $("#confirmModal").modal("show");
      } else {
        $("#confirmModal").data("page", "/my_tutors");
        window.location.href = $("#confirmModal").data("page");
      }
    }
  });

  $("#btn_home").click(function () {
    if (isEmptyTutor()) {
      $("#confirmModal").data("page", "/home");
      window.location.href = $("#confirmModal").data("page");
    } else {
      if (isSaved == 0) {
        $("#confirmModal").modal("show");
      } else {
        $("#confirmModal").data("page", "/home");
        window.location.href = $("#confirmModal").data("page");
      }
    }
  });


  $("#btn_myProfile").click(function () {
    if (isEmptyTutor()) {
      $("#confirmModal").data("page", "/profile");
      window.location.href = $("#confirmModal").data("page");
    } else {
      if (isSaved == 0) {
        $("#confirmModal").modal("show");
      } else {
        $("#confirmModal").data("page", "/profile");
        window.location.href = $("#confirmModal").data("page");
      }
    }
  });

  $("#btn_cancel").click(function () {
    $("#confirmModal").modal("hide");
  });

  $("#btn_save_tutor_header").click(function () {
    save_tutor();
    var a = $("#confirmModal").data("page");
    //console.log(a);
    window.location.href = $("#confirmModal").data("page");
  });

  $("#save_tutor").click(function () {
    save_tutor();
  });

  $("#train_tutor").click(function () {
    if (isSaved == 0) {
      $("#TrainModal").modal("show");
    } else {
      if (trainID == 0 || trainID == null) {
      } else {
        Id = $(this).parents("tr").find("td").eq(0).html();

        var data = {
          Id: trainID,
        };

        $.ajax({
          url: "/tutor_train",
          dataType: "json",
          data: JSON.stringify(data),
          type: "POST",
          contentType: "application/json",
          success: function (response) {
            //console.log("response=========", JSON.stringify(response));
            window.location.href = "/train";

            localStorage.setItem("content", response.tutor);
            localStorage.setItem("tutor_id", response.tutor_id);

            //console.log( $('#page').html())
            $("#page").replaceWith(response.tutor);
          },
          error: function (error) {
            //console.log(error);
          },
        });
      }
    }
  });

  $("#preview_tutor").click(function () {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });

    document.getElementById("drag_drop").style.display = "none";

    $("#title-font").text("Preview Tutor");
    $("#title-font").css("color", "#0d6efd");

    if ($("#btn_back_edit").length > 0) {
      //console.log("already exist!!!");
    } else {
      $("#tutor-title").append(
        '<button class="btn btn-dark" style="margin-top: 8px;" id="btn_back_edit">Back To Tutor Edit Mode</button>'
      );
    }

    //console.log("This is preview_tutor");

    var str = $(".list p.page-item").text();

    //console.log("str", str);

    $(".list p.page-item").each(function () {
      // For each element
      if ($(this).text().trim() === "")
        // $(this).remove(); // if it is empty, it removes it
        $(this).replaceWith(
          $(
            '<input style = "width: 100%; height: 100%; border: none!important; background: none;" class="page-item">' +
            "</input>"
          )
        );
    });

    $("#btn_back_edit").click(function () {
      //console.log("This is edit mode!!!!!!!");
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
      document.getElementById("drag_drop").style.display = "block";
      $("#title-font").text("Tutor Builder");
      $("#title-font").css("color", "black");

      $(".list input.page-item").replaceWith(
        $('<p class="page-item" id = "page-item">' + "</p>")
      );

      $("#btn_back_edit").remove();
    });
  });

  const CLASS_NAMES = {
    // guideLine: "__sortable_draggable-guide-line"
  };
  const containerStack = [];

  let dragItem;
  let copyItem;

  let dropTarget;
  let copyTarget;

  let sourceContainer;
  let data = null;
  let EditItem;
  let copyMode = false;

  // Initialize the dictionary to store item counts
  var componentCounts = { "Component 1": 0 };
  /**
   * Increments the count of a specific component within a global dictionary (`componentCounts`).
   * If the component is not already present in the dictionary, it is added with an initial count of 1.
   * This function is useful for tracking the usage or occurrence of various components within an application.
   *
   * @param {string} componentName - The name of the component to be incremented in the count.
   */
  function incrementComponentCount(componentName) {
    // If the component is already in the dictionary, increment its count
    if (componentCounts.hasOwnProperty(componentName)) {
      componentCounts[componentName]++;
    } else {
      // Otherwise, add the component to the dictionary with an initial count of 1
      componentCounts[componentName] = 1;
    }
  }

  let dummyElement = document.createElement("div");
  dummyElement.className += "dummy";

  class Dragoned {
    constructor(container, options = {}) {
      if (typeof container === "string") {
        container = document.querySelector(container);
      }
      if (!container || !container instanceof HTMLElement) {
        return new Error(
          "Dragoned: container must be a string or an HTMLElement"
        );
      }
      this.dragOverHandler = this.dragOverHandler.bind(this);
      this.container = container;
      this.moveY = 0;
      this.moveX = 0;
      this.mouseUp = false;
      this.optionsInit(options);
      containerStack.push(this);
      this.init();
    }

    optionsInit(options) {
      this.options = {
        draggable: options.draggable,
        handle: options.handle,
        delay: typeof options.delay === "number" ? options.delay : 0,
        preventDefault: options.preventDefault,
        direction: options.direction,
        onStart: options.onStart,
        onMove: options.onMove,
        onClone: options.onClone,
        onEnd: options.onEnd,
        body: options.body || document.body,
        clone: options.clone,
        group: options.group,
        sort: options.sort,
      };
    }

    init() {
      this.bindDrag(this.container);
    }

    bindDrag(container) {
      container.style.userSelect = "none";
      container.addEventListener("dragover", this.dragOverHandler);
    }

    dragOverHandler(event) {
      event.preventDefault();

      if (
        event.target.nodeName == "UL" &&
        event.target.dataset.type === dragItem.dataset.type
      ) {
        dummyElement.classList.add("dummy");
        //event.target.append(dummyElement);
        dropTarget = event.target;
      } else {
        // dropTarget = null;
        // $('.dummy').remove();
        // event.target.removeChild(dummyElement);
        dragItem.classList.remove("active");
      }
    }
  }

  class Dragoned_Component {
    constructor(container, options = {}) {
      if (typeof container === "string") {
        container = document.querySelector(container);
      }
      if (!container || !container instanceof HTMLElement) {
        return new Error(
          "Dragoned: container must be a string or an HTMLElement"
        );
      }
      this.dragOverHandler = this.dragOverHandler.bind(this);
      this.copyOverHandler = this.copyOverHandler.bind(this);

      this.container = container;
      this.moveY = 0;
      this.moveX = 0;
      this.mouseUp = false;
      this.optionsInit(options);
      containerStack.push(this);
      this.init();
    }
    optionsInit(options) {
      this.options = {
        draggable: options.draggable,
        handle: options.handle,
        delay: typeof options.delay === "number" ? options.delay : 0,
        preventDefault: options.preventDefault,
        direction: options.direction,
        onStart: options.onStart,
        onMove: options.onMove,
        onClone: options.onClone,
        onEnd: options.onEnd,
        body: options.body || document.body,
        clone: options.clone,
        group: options.group,
        sort: options.sort,
      };
    }

    init() {
      this.bindDrag(this.container);
    }

    bindDrag(container) {
      container.style.userSelect = "none";
      container.addEventListener("dragover", this.dragOverHandler);
      container.addEventListener('mouseover', this.copyOverHandler)
    }

    copyOverHandler(event) {
      event.preventDefault();
      if (!copyMode) return;

      // Determine if the current drag over event target matches the conditions
      if (
        (event.target.nodeName === "UL" &&
          event.target.dataset.type === copyItem.dataset.type) ||
        (event.target.classList.contains("page-item-ul") &&
          copyItem.classList.contains("btn-column")) ||
        (event.target.id === "page-container" && copyItem.classList.contains("btn-row")) ||
        (event.target.classList.contains("component-details-content") &&
          (copyItem.id === "row-item" || copyItem.id === "column-item")) ||
        (event.target.id === "page-container" &&
          copyItem.id.startsWith("galleryItem_"))
      ) {
        let targetContainer = event.target;

        // Determine the correct container for inserting the dummyElement
        if (
          targetContainer.id === "page-container" &&
          copyItem.classList.contains("btn-row")
        ) {
          targetContainer = document.querySelector("#page-container");
        } else if (
          targetContainer.classList.contains("component-details-content")
        ) {
          targetContainer = event.target;
        }

        let insertBeforeElement = null;
        // Get the list of all child elements within the target container
        const listItems = Array.from(targetContainer.children);
        if (targetContainer.classList.contains("page-item-rl-row")) {
          // Find the child element to insert the dummy element before
          for (const item of listItems) {
            const rect = item.getBoundingClientRect();
            const halfwayPoint = rect.y + rect.height / 2;

            // Check if the mouse pointer is above the halfway point of the child element
            if (event.clientY < halfwayPoint) {
              insertBeforeElement = item;
              break;
            }
          }
        }
        else if (targetContainer.classList.contains("page-item-ul")) {
          for (const item of listItems) {
            const rect = item.getBoundingClientRect();
            const halfwayPoint = rect.x + rect.width / 2; // Change to calculate the horizontal halfway point

            // Check if the mouse pointer is to the left of the halfway point of the child element
            if (event.clientX < halfwayPoint) {
              insertBeforeElement = item;
              break; // Found the target item, stop looping
            }
          }
        }

        // Add the dummy element class
        dummyElement.classList.add("dummy");

        // Insert the dummy element at the determined position
        if (insertBeforeElement) {
          targetContainer.insertBefore(dummyElement, insertBeforeElement);
        } else {
          // If no insertBeforeElement is found (e.g., dragging below all items), append to the end
          targetContainer.appendChild(dummyElement);
        }

        copyTarget = targetContainer;
      } else {
        // If the drag over target doesn't match any of the specified conditions
      }
    }
    dragOverHandler(event) {
      event.preventDefault();

      // Determine if the current drag over event target matches the conditions
      if (
        (event.target.nodeName === "UL" &&
          event.target.dataset.type === dragItem.dataset.type) ||
        (event.target.classList.contains("page-item-ul") &&
          dragItem.classList.contains("btn-column")) ||
        (event.target.id === "page-container" && dragItem.classList.contains("btn-row")) ||
        (event.target.classList.contains("component-details-content") &&
          (dragItem.id === "row-item" || dragItem.id === "column-item")) ||
        (event.target.id === "page-container" &&
          dragItem.id.startsWith("galleryItem_"))
      ) {
        let targetContainer = event.target;

        // Determine the correct container for inserting the dummyElement
        if (
          targetContainer.id === "page-container" &&
          dragItem.classList.contains("btn-row")
        ) {
          targetContainer = document.querySelector("#page-container");
        } else if (
          targetContainer.classList.contains("component-details-content")
        ) {
          targetContainer = event.target;
        }

        let insertBeforeElement = null;
        // Get the list of all child elements within the target container
        const listItems = Array.from(targetContainer.children);
        if (targetContainer.classList.contains("page-item-rl-row")) {
          // Find the child element to insert the dummy element before
          for (const item of listItems) {
            const rect = item.getBoundingClientRect();
            const halfwayPoint = rect.y + rect.height / 2;

            // Check if the mouse pointer is above the halfway point of the child element
            if (event.clientY < halfwayPoint) {
              insertBeforeElement = item;
              break;
            }
          }
        }
        else if (targetContainer.classList.contains("page-item-ul")) {
          for (const item of listItems) {
            const rect = item.getBoundingClientRect();
            const halfwayPoint = rect.x + rect.width / 2; // Change to calculate the horizontal halfway point

            // Check if the mouse pointer is to the left of the halfway point of the child element
            if (event.clientX < halfwayPoint) {
              insertBeforeElement = item;
              break; // Found the target item, stop looping
            }
          }
        }

        // Add the dummy element class
        dummyElement.classList.add("dummy");

        // Insert the dummy element at the determined position
        if (insertBeforeElement) {
          targetContainer.insertBefore(dummyElement, insertBeforeElement);
        } else {
          // If no insertBeforeElement is found (e.g., dragging below all items), append to the end
          targetContainer.appendChild(dummyElement);
        }

        dropTarget = targetContainer;
      } else {
        // If the drag over target doesn't match any of the specified conditions
        dragItem.classList.remove("active");
      }
    }


  }

  function appendToLocalLog(logEntry) {
    let currentLog = localStorage.getItem('experimentLog') || '';
    currentLog += JSON.stringify(logEntry) + '\n';
    localStorage.setItem('experimentLog', currentLog);
  }
  
  function create_log_item(component, actor, actor_id, action_type, action_value) {
    const logItem = {
      time_stamp: new Date().toLocaleString(),
      component: component,
      actor: actor,
      actor_id: actor_id,
      action_type: action_type,
      action_value: action_value
    };
  
    appendToLocalLog(logItem);
  
    return logItem;
  }



  window.addEventListener("DOMContentLoaded", (event) => {
    (function () {



      let currentStep = 0;
      let currentLayout = false;

      let step1Text = '';
      let step2Text = '';
      let generatedSteps = [];
      let aiGuidedActive = false
      let stepsContainer;
      let generatedDrafts = [];
      let currentTutor = false

      let activeCursor = null;
      let isPinLayout = false;
      let isLikeLayout = false;

      initOrResume();


      function editPlaceholder(input) {
        const currentPlaceholder = input.placeholder;
        const newPlaceholder = prompt("Enter new placeholder:", currentPlaceholder);

        if (newPlaceholder !== null) {
          input.placeholder = newPlaceholder;
        }
      }

      document.addEventListener("dblclick", function (e) {
        // Check if the clicked target is a component name or a page item
        if (e.target.classList.contains("component-name") || e.target.classList.contains("page-item")) {
          // Make the target content editable and focus on it for immediate editing
          e.target.contentEditable = true;
          e.target.focus();

          // Add a one-time event listener for blur to handle when the editing is finished
          e.target.addEventListener("blur", function handler() {
            // Assuming the logic to determine and update the correct element goes here
            // Example: Update the element's innerHTML with the new text
            e.target.innerText = e.target.innerText; // Simplified; adapt as needed

            // Disable contentEditable
            e.target.contentEditable = false;
            // Remove this blur event listener after it's executed
            e.target.removeEventListener("blur", handler);
          }, { once: true }); // The listener is removed after execution thanks to {once: true}
        }
        if (e.target.classList.contains("form-control")) {
          // Add double-click event listener to each form control
          editPlaceholder(e.target);
        }
      });

      document.addEventListener("dragstart", dragStartHandler, false);
      document.addEventListener("dragend", dragEndHandler, false);
      document.addEventListener("drop", dropHandler, false);
      document
        .getElementById("page")
        .addEventListener("click", onClickHandler, false);
      // Select all elements with the 'component-details-container' class
      document
        .querySelectorAll(".component-details-container")
        .forEach((container) => {
          container.addEventListener("click", onClickHandler, false);
        });
        
      document.getElementById("redo").addEventListener("click", redo, false);
      document.getElementById("undo").addEventListener("click", undo, false);
      document.getElementById("restart").addEventListener("click", restart, false);
      document.getElementById('saveLogButton').addEventListener('click', function() {
        const logContent = localStorage.getItem('experimentLog') || '';
        
        // Create a Blob with the log content
        const blob = new Blob([logContent], { type: 'text/plain' });
        
        // Create a temporary URL for the Blob
        const url = window.URL.createObjectURL(blob);
        
        // Create a link element and trigger the download
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'experiment_log.txt';
        
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      });
      // Event listeners for the buttons
      document.getElementById("show-td").addEventListener("click", function () {
        toggleSection("show-td", "ai-tutor-designer");
      });
      document.getElementById("show-cg").addEventListener("click", function () {
        toggleSection("show-cg", "components-gallery"); // Use the actual ID for the Components Gallery section
      });
      document.getElementById("show-dd").addEventListener("click", function () {
        toggleSection("show-dd", "drag-drop-section"); // Use the actual ID for the Drag and Drop section
      });

      toggleSection("show-cg", "components-gallery")
      toggleSection("show-td", "ai-tutor-designer")
      // Initialize sections to be visible or hidden
      // Initialize other sections similarly with their respective IDs
      // document.getElementById('components-gallery').style.display = 'none';
      // document.getElementById('drag-drop-section').style.display = 'none';
      // document.getElementById('editor-section').style.display = 'none';

      function sendMessage() {
        var inputField = document.getElementById('userInput');
        var userText = inputField.value.trim();
        if (userText !== "") {
          if (userText.toLowerCase().includes('component')) {
            sendComponentResponse();
          } else {
            // Display user message
            addMessageToChat("user", userText);

            // Simulate bot response
            addMessageToChat("bot", "Thank you for your message!");

            // Clear the input field
            inputField.value = "";
          }
        }
      }
      document.getElementById('sendButton').addEventListener('click', function () {

        sendMessage();


      });



      document.getElementById('userInput').addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === 'Return') {
          event.preventDefault();  // Prevents the default action of Enter (form submission or newline)
          sendMessage();
        }
      });



      function sendComponentResponse() {
        var chatMessages = document.querySelector('.chat-messages');
        var componentHtml = `<div class="btn btn-info btn-column drop-box rounded-button" data-type="page-items" draggable="true" type="button" id="galleryItem_Component 1_10"><p class="removeFromDom">Column</p><ul class="list one d-flex flex-column gap-2 page-item-rl-row" data-type="page-row"><div class="btn btn-success btn-label row rounded-button" data-type="page-row" draggable="true" type="button" id="galleryItem_Component 1_3"><p class="page-item align-self-center">Rational Equation</p><p class="removeFromDom">Label</p></div><div class="btn btn-warning btn-row btn-row-item grid drop-box rounded-button" data-type="page-row" draggable="true" type="button" id="galleryItem_Component 1_9"><p class="removeFromDom">Row</p><ul class="list one page-item-ul grid grid-flow-col gap-1" data-type="page-row"><div class="btn btn-light btn-input-box-t rounded-button" data-type="page-row" draggable="true" type="button" id="galleryItem_Component 1_4"><input class="form-control" placeholder="Rational Coefficient 1" style="border: none;box-shadow: none;text-align: center;"></div><div class="btn btn-success btn-label row rounded-button" data-type="page-row" draggable="true" type="button" id="galleryItem_Component 1_5"><p class="page-item align-self-center">/</p><p class="removeFromDom">Label</p></div><div class="btn btn-light btn-input-box-t rounded-button" data-type="page-row" draggable="true" type="button" id="galleryItem_Component 1_6"><input class="form-control" placeholder="Rational Coefficient 2" style="border: none;box-shadow: none;text-align: center;"></div><div class="btn btn-success btn-label row rounded-button" data-type="page-row" draggable="true" type="button" id="galleryItem_Component 1_7"><p class="page-item align-self-center">=</p><p class="removeFromDom">Label</p></div><div class="btn btn-light btn-input-box-t rounded-button" data-type="page-row" draggable="true" type="button" id="galleryItem_Component 1_8"><input class="form-control" placeholder="Rational Result" style="border: none;box-shadow: none;text-align: center;"></div></ul></div></ul></div>`;
        var componentHtml = `<div class="generated-component">${componentHtml}</div>`;

        var messageDiv = document.createElement('div');
        messageDiv.innerHTML = componentHtml;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the latest message
      }




      // Event listener for close button


      function saveState() {
        const state = {
          currentStep: currentStep,
          currentLayout: currentLayout,
          step1Text: step1Text,
          step2Text: step2Text,
          generatedSteps: generatedSteps,
          stepsContainerHTML: (stepsContainer && stepsContainer.innerHTML),
          generatedDrafts: generatedDrafts ?? [],
          aiGuidedActive: true,
          currentTutor: currentTutor,
        };
        localStorage.setItem('aiGuidedState', JSON.stringify(state));
      }

      function loadState() {
        const savedState = JSON.parse(localStorage.getItem('aiGuidedState'));
        return savedState || null;
      }




      function initOrResume() {


        // Close modal function
        function closeModal() {
          const draftModal = document.getElementById("draftModal");
          draftModal.style.display = "none";
        }

        function toggleLock(stepBox, input, lockButton) {
          const isLocked = lockButton.querySelector('i').classList.contains('fa-lock');
          if (isLocked) {
            // Unlock
            lockButton.innerHTML = '<i class="fas fa-lock-open"></i>';
            stepBox.classList.remove('locked');
          } else {
            // Lock
            lockButton.innerHTML = '<i class="fas fa-lock"></i>';
            stepBox.classList.add('locked');
          }
        }

        // Function to add a new step box
        function addStepBox(text = "", referenceStepBox = null) {
          const stepBox = document.createElement('div');
          const buttons_container = document.createElement('div');

          stepBox.id = `stepBox_${stepCounter++}`;
          stepBox.classList.add('step-box', 'inactive');

          const buttonsContainer = document.createElement('div');
          buttonsContainer.classList.add('buttons-container');

          const deleteButton = document.createElement('button');
          deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
          deleteButton.classList.add('delete-button', 'btn', 'btn-danger');
          deleteButton.onclick = () => {
            if (stepsContainer.childElementCount > 1) {
              deleteStepBox(stepBox);
            }
          };
          buttonsContainer.appendChild(deleteButton);

          const lockButton = document.createElement('button');
          lockButton.innerHTML = '<i class="fas fa-lock-open"></i>';
          lockButton.classList.add('lock-button', 'btn', 'btn-secondary');
          lockButton.onclick = () => toggleLock(stepBox, input, lockButton);
          buttonsContainer.appendChild(lockButton);



          const input = document.createElement('textarea');
          input.value = text || "Enter step details here...";
          input.readOnly = false;
          stepBox.appendChild(input);
          buttons_container.appendChild(buttonsContainer);
          buttons_container.classList.add('b-container');
          const addButton = document.createElement('button');
          addButton.innerHTML = '<i class="fas fa-plus"></i>';
          addButton.classList.add('add-button', 'btn', 'btn-primary');
          addButton.onclick = () => addStepBox("", stepBox);
          buttons_container.appendChild(addButton);
          stepBox.appendChild(buttons_container);

          if (referenceStepBox) {
            referenceStepBox.parentNode.insertBefore(stepBox, referenceStepBox.nextSibling);
          } else {
            stepsContainer.appendChild(stepBox);
          }
          updateDeleteButtonState();

          return stepBox;
        }

        // Function to delete a step box
        function deleteStepBox(stepBox) {
          stepsContainer.removeChild(stepBox);
          updateDeleteButtonState();
          return stepBox;
        }
        function getLockedSteps() {
          const stepBoxes = stepsContainer.querySelectorAll('.step-box');
          return Array.from(stepBoxes).map((stepBox, index) => ({
            step: stepBox.querySelector('textarea').value,
            isLocked: stepBox.classList.contains('locked'),
            index: index
          })).filter(step => step.isLocked);
        }
        function updateDeleteButtonState() {
          const deleteButtons = document.querySelectorAll('.delete-button');
          deleteButtons.forEach(button => {
            if (stepsContainer.childElementCount === 1) {
              button.classList.add('disabled');
            } else {
              button.classList.remove('disabled');
            }
          });
        }
        // Function to update the textarea content and button visibility
        function updateStep() {
          if (currentStep === 1 || currentStep === 2) {
            // Hide the third step

            stepsContainer.style.display = 'none';
            regenButton.classList.add("hidden");
            luckyButton.classList.add("hidden");
            aiSpecsTextarea.style.display = 'block';
            aiSpecsFrame.classList.remove("extra-expanded");
            draftModal.classList.remove("extra-expanded");
            aiSpecsButtonContainer.classList.remove("extra-expanded")
            if (currentStep === 1) {
              aiSpecsTextarea.placeholder = "Enter the initial question here...";
              backButton.style.display = 'none'; // Hide "Back" on first step
              aiSpecsTextarea.value = step1Text;
            } else {
              aiSpecsTextarea.placeholder = "Enter additional instructions or questions here...";
              backButton.style.display = 'block';
              aiSpecsTextarea.value = step2Text;

            }
            cancelButton.style.display = 'block';
            nextButton.style.display = 'block';
            nextButton.textContent = "Next"; // Reset "Next" button text

          } else if (currentStep === 3) {
            // Show the third step
            aiSpecsFrame.classList.add("extra-expanded");
            draftModal.classList.add("extra-expanded");
            aiSpecsButtonContainer.classList.add("extra-expanded");
            regenButton.classList.remove("hidden");
            luckyButton.classList.remove("hidden");

            regenButton.onclick = regenerateSteps;
            aiSpecsTextarea.style.display = 'none';
            nextButton.textContent = "Generate Tutor Drafts"
            nextButton.onclick = generateLayoutDrafts;
            backButton.style.display = 'block';
            stepsContainer.style.display = 'flex';
            // Add Regenerate button
            // Add Regenerate but
            if (generatedSteps.length === 0) {
              // Only add the initial step if there are no generated steps
              addStepBox();
            } else {
              // Add the generated steps to the stepsContainer
              generatedSteps.forEach(step => {
                addStepBox(step);
              });
            }
          } else {
            closeModal();
          }
        }


        function toggleCursor(cursorType, button) {
          const buttons = document.querySelectorAll('.btn, .form-control');

          if (activeCursor === cursorType) {
            // Deactivate the current cursor
            buttons.forEach(btn => {
              btn.classList.remove(`${activeCursor}-cursor`);
            });
            if (button) {
              button.classList.remove('active');
            }
            activeCursor = null;
            isPinLayout = false;
            isLikeLayout = false;
          } else {
            // Deactivate the previous cursor if any
            if (activeCursor) {
              buttons.forEach(btn => {
                btn.classList.remove(`${activeCursor}-cursor`);
              });
              const activeButton = document.querySelector('.bottom-bar button.active');
              if (activeButton) activeButton.classList.remove('active');
            }
            // Activate the new cursor
            buttons.forEach(btn => {
              btn.classList.add(`${cursorType}-cursor`);
            });
            if (button) {
              button.classList.add('active');
            }
            activeCursor = cursorType;
            isPinLayout = cursorType === 'pinning';
            isLikeLayout = cursorType === 'liking';

          }

          selectedElements.forEach(el => el.classList.remove("clicked"));
          selectedElements = [];
        }
        function pinLayout(event) {
          cleanSelected();
          toggleCursor('pinning', event.target);
        }

        function likeLayout(event) {
          cleanSelected();
          toggleCursor('liking', event.target);
        }
        function useLayout(index) {
          // Implement use layout functionality
        }
        function generateFromPreferences() {
          console.log('Generating from preferences');

          // Filter the generatedDrafts array to include only drafts with pointed attribute
          const draftsWithPointed = generatedDrafts.filter(draft => {
            const parser = new DOMParser();
            const htmlDoc = parser.parseFromString(draft, 'text/html');
            const elementsWithPointed = htmlDoc.querySelectorAll('[pointed]');
            return elementsWithPointed.length > 0;
          });

          if (draftsWithPointed.length === 0) {
            alert('No preference expressed. Please select preferred elements before generating from preferences.');
            return;
          }

          const spinnerOverlay = document.createElement('div');

          spinnerOverlay.classList.add('spinner-overlay');

          const layoutContainer = document.getElementById('full-layout-container');
          spinnerOverlay.innerHTML = '<div class="spinner"></div>';
          layoutContainer.appendChild(spinnerOverlay);

          fetch('/generateFromPreferences', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              drafts: draftsWithPointed
            })
          })
            .then(response => response.json())
            .then(data => {
              layoutContainer.removeChild(spinnerOverlay);
              const pageContainer = document.getElementById('page-container');
              pageContainer.innerHTML = buildHTMLFromCompactRepresentation(data.text, false); // Clear existing content
              toggleCursor(activeCursor, false)

              const element = document.getElementById('playground');
              // Remove the width style property
              element.style.width = '70%';


              document.getElementById("drag_drop").classList.remove("display-none")
              document.getElementById("drag-drop-section").classList.remove("display-none")
              document.getElementById("control-bar").classList.remove("hidden")


              currentTutor = pageContainer.innerHTML
              saveState()
            })
            .catch(error => {
              console.error('Error:', error);
              layoutContainer.removeChild(spinnerOverlay);
            });
        }
        function generateFullLayout() {
          const fullLayoutContainer = document.createElement('div');
          fullLayoutContainer.id = 'full-layout-container';
          fullLayoutContainer.classList.add('full-layout-container');

          const navigationBar = document.createElement('div');
          navigationBar.classList.add('navigation-bar');

          const backButton = document.createElement('button');
          backButton.textContent = 'Back to Grid';
          backButton.onclick = function () {
            hideFullLayout();
            currentLayout = false;
            saveState()
          }
          navigationBar.appendChild(backButton);

          const titleContainer = document.createElement('div');
          titleContainer.classList.add('title-container');

          const leftArrow = document.createElement('button');
          leftArrow.textContent = '←';
          leftArrow.onclick = function () {
            generatedDrafts[currentLayoutIndex] = layoutContent.innerHTML
            navigateLayout(-1);
          }
          titleContainer.appendChild(leftArrow);

          const layoutTitle = document.createElement('h2');
          layoutTitle.id = 'layout-title';
          titleContainer.appendChild(layoutTitle);

          const rightArrow = document.createElement('button');
          rightArrow.textContent = '→';
          rightArrow.onclick = function () {
            generatedDrafts[currentLayoutIndex] = layoutContent.innerHTML
            navigateLayout(1);
          }
          titleContainer.appendChild(rightArrow);

          navigationBar.appendChild(titleContainer);
          fullLayoutContainer.appendChild(navigationBar);

          const layoutContent = document.createElement('div');
          layoutContent.id = 'layout-content';
          layoutContent.classList.add('full-layout-content');
          fullLayoutContainer.appendChild(layoutContent);

          const bottomBar = document.createElement('div');
          bottomBar.classList.add('bottom-bar');

          const leftButtonGroup = document.createElement('div');
          leftButtonGroup.classList.add('button-group');

          const pinButton = document.createElement('button');
          pinButton.textContent = 'Pin';
          pinButton.onclick = (event) => pinLayout(event);
          leftButtonGroup.appendChild(pinButton);

          const likeButton = document.createElement('button');
          likeButton.textContent = 'I Like';
          likeButton.onclick = (event) => likeLayout(event);
          leftButtonGroup.appendChild(likeButton);

          const rightButtonGroup = document.createElement('div');
          rightButtonGroup.classList.add('button-group');

          const useLayoutButton = document.createElement('button');
          useLayoutButton.textContent = 'Use This Layout';
          useLayoutButton.onclick = useLayout;
          rightButtonGroup.appendChild(useLayoutButton);

          const generateFromPreferencesButton = document.createElement('button');
          generateFromPreferencesButton.textContent = 'Generate from Preferences';
          generateFromPreferencesButton.onclick = function () {
            generatedDrafts[currentLayoutIndex] = layoutContent.innerHTML
            generateFromPreferences()
          }
          rightButtonGroup.appendChild(generateFromPreferencesButton);

          bottomBar.appendChild(leftButtonGroup);
          bottomBar.appendChild(rightButtonGroup);

          fullLayoutContainer.appendChild(bottomBar);

          return fullLayoutContainer

        }




        let currentLayoutIndex = false;
        let fullLayoutContainer;


        function showFullLayout(index) {
          currentLayoutIndex = index;
          const pageContainer = document.getElementById('page-container');
          pageContainer.innerHTML = ''; // Clear existing content
          if (!fullLayoutContainer) {
            fullLayoutContainer = generateFullLayout();
          }

          const layoutContent = fullLayoutContainer.querySelector('#layout-content');
          const layoutTitle = fullLayoutContainer.querySelector('#layout-title');

          layoutContent.innerHTML = generatedDrafts[index];
          layoutTitle.textContent = `Layout ${index + 1}`;
          pageContainer.appendChild(fullLayoutContainer);

          // Reset cursor state
          activeCursor = null;
          isPinLayout = false;
          isLikeLayout = false;
          const buttons = document.querySelectorAll('.btn, .form-control');
          buttons.forEach(btn => {
            btn.classList.remove('pinning-cursor', 'liking-cursor');
          });
          const activeButtons = document.querySelectorAll('.bottom-bar button.active');
          activeButtons.forEach(btn => btn.classList.remove('active'));
        }

        function hideFullLayout() {
          const pageContainer = document.getElementById('page-container');
          pageContainer.innerHTML = ''; // Clear existing content
          loadLayoutDraft()
        }

        function navigateLayout(direction) {
          const newIndex = (currentLayoutIndex + direction + generatedDrafts.length) % generatedDrafts.length;
          const layoutContent = document.getElementById('layout-content');
          const layoutTitle = document.getElementById('layout-title');

          currentLayoutIndex = newIndex;
          layoutContent.innerHTML = generatedDrafts[newIndex];
          layoutTitle.textContent = `Layout ${newIndex + 1}`;

          // Reapply the active cursor if there is one
          if (activeCursor) {
            const buttons = document.querySelectorAll('.btn, .form-control');
            buttons.forEach(btn => {
              btn.classList.add(`${activeCursor}-cursor`);
            });
            const activeButton = document.querySelector(`.bottom-bar button[onclick*="${activeCursor}"]`);
            if (activeButton) activeButton.classList.add('active');
          }
        }

        function loadLayoutDraft() {
          const gridContainer = document.createElement('div');
          gridContainer.classList.add('grid-container');

          generatedDrafts.forEach((layout, index) => {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');

            const layoutContent = document.createElement('div');
            layoutContent.classList.add('layout-content');

            const miniatureWrapper = document.createElement('div');
            miniatureWrapper.classList.add('miniature-wrapper');
            miniatureWrapper.innerHTML = layout;

            layoutContent.appendChild(miniatureWrapper);

            const layoutTitle = document.createElement('div');
            layoutTitle.classList.add('layout-title');
            layoutTitle.textContent = `Layout ${index + 1}`;

            gridItem.appendChild(layoutTitle);
            gridItem.appendChild(layoutContent);
            gridItem.onclick = function () {
              showFullLayout(index);
              currentLayout = index
              saveState()
              // Implement the logic to generate a new layout here
            };

            gridContainer.appendChild(gridItem);
          });

          // Add the "add layout" grid item
          const addLayoutItem = document.createElement('div');
          addLayoutItem.classList.add('grid-item', 'add-layout-item');
          addLayoutItem.innerHTML = '<span>+</span>';
          addLayoutItem.onclick = function () {
            console.log('Add new layout clicked');
            // Implement the logic to generate a new layout here
          };
          gridContainer.appendChild(addLayoutItem);

          const pageContainer = document.getElementById('page-container');
          pageContainer.innerHTML = ''; // Clear existing content
          pageContainer.appendChild(gridContainer);
        }


        function generateLayoutDrafts() {




          const currentSteps = Array.from(stepsContainer.querySelectorAll('.step-box textarea'))
            .map(textarea => textarea.value);

          const spinnerOverlay = document.createElement('div');
          spinnerOverlay.classList.add('spinner-overlay');
          spinnerOverlay.innerHTML = '<div class="spinner"></div>';
          aiSpecsFrame.appendChild(spinnerOverlay);

          fetch('/generateTutorLayoutsFromSteps', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              text: step2Text,
              steps: currentSteps
            })
          })
            .then(response => response.json())
            .then(data => {
              aiSpecsFrame.removeChild(spinnerOverlay);

              const gridContainer = document.createElement('div');
              gridContainer.classList.add('grid-container');

              data.layouts.forEach((layout, index) => {
                const gridItem = document.createElement('div');
                gridItem.classList.add('grid-item');

                const layoutContent = document.createElement('div');
                layoutContent.classList.add('layout-content');

                const miniatureWrapper = document.createElement('div');
                miniatureWrapper.classList.add('miniature-wrapper');
                html_layout = buildHTMLFromCompactRepresentationND(layout);
                miniatureWrapper.innerHTML = html_layout

                generatedDrafts.push(html_layout)

                layoutContent.appendChild(miniatureWrapper);

                const layoutTitle = document.createElement('div');
                layoutTitle.classList.add('layout-title');
                layoutTitle.textContent = `Layout ${index + 1}`;

                gridItem.appendChild(layoutTitle);
                gridItem.appendChild(layoutContent);
                gridItem.onclick = function () {
                  showFullLayout(index);
                  currentLayout = index
                  saveState()
                  // Implement the logic to generate a new layout here
                };
                gridContainer.appendChild(gridItem);
              });

              // Add the "add layout" grid item
              const addLayoutItem = document.createElement('div');
              addLayoutItem.classList.add('grid-item', 'add-layout-item');
              addLayoutItem.innerHTML = '<span>+</span>';
              addLayoutItem.onclick = function () {
                console.log('Add new layout clicked');
                // Implement the logic to generate a new layout here
              };
              gridContainer.appendChild(addLayoutItem);

              const pageContainer = document.getElementById('page-container');
              pageContainer.innerHTML = ''; // Clear existing content
              pageContainer.appendChild(gridContainer);
              currentStep = 4;
              closeModal();
              saveState()
            })
            .catch(error => {
              console.error('Error:', error);
              aiSpecsFrame.removeChild(spinnerOverlay);
            });
        }

        function parseSteps(response) {
          // Remove any "Steps:" prefix and split by comma or newline
          const stepsString = response.replace(/^Steps:\s*/, '');
          const stepsArray = stepsString.split(/,|\n/).map(step => step.trim());

          // Parse each step
          const parsedSteps = stepsArray
            .map(step => {
              // Remove the numbering and any leading/trailing whitespace
              const withoutNumber = step.replace(/^\d+\.\s*/, '').trim();

              // Capitalize the first letter (in case it's not)
              return withoutNumber.charAt(0).toUpperCase() + withoutNumber.slice(1);
            })
            .filter(step => step.length > 0); // Remove any empty steps

          return parsedSteps;
        }

        function regenerateSteps() {
          // Store current steps in previousGeneratedSteps array
          if (generatedSteps.length > 0) {
            previousGeneratedSteps.push([...generatedSteps]);
          }

          // Show spinner overlay
          const spinnerOverlay = document.createElement('div');
          spinnerOverlay.classList.add('spinner-overlay');
          spinnerOverlay.innerHTML = '<div class="spinner"></div>';
          aiSpecsFrame.appendChild(spinnerOverlay);

          const lockedStepsInfo = getLockedSteps();
          const lockedSteps = lockedStepsInfo.map(info => info.step);
          const endpoint = lockedSteps.length > 0 ? '/generateLockedSteps' : '/generateTutorSteps';

          // Call API to regenerate steps
          fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              text: step2Text,
              lockedSteps: lockedSteps
            })
          })
            .then(response => response.json())
            .then(data => {
              const steps = data.steps;
              const parsedSteps = parseSteps(steps);

              // Clear current steps
              while (stepsContainer.firstChild) {
                stepsContainer.removeChild(stepsContainer.firstChild);
              }

              generatedSteps = parsedSteps;

              // Add steps, preserving locked status based on content
              parsedSteps.forEach((step) => {
                const stepBox = addStepBox(step);
                const matchingLockedStep = lockedStepsInfo.find(info => info.step === step);
                if (matchingLockedStep) {
                  const lockButton = stepBox.querySelector('.lock-button');
                  if (lockButton) {
                    toggleLock(stepBox, stepBox.querySelector('textarea'), lockButton);
                  }
                }
              });

              // Hide spinner overlay
              aiSpecsFrame.removeChild(spinnerOverlay);
            })
            .catch(error => {
              console.error('Error:', error);
              aiSpecsFrame.removeChild(spinnerOverlay);
            });
        }


        function nextStep() {
          if (currentStep === 1) {
            step1Text = aiSpecsTextarea.value;
            currentStep++;
            saveState()
            updateStep();
          } else if (currentStep === 2) {
            step2Text = aiSpecsTextarea.value;
            if (generatedSteps.length === 0) {
              // Show spinner overlay in step 2
              const spinnerOverlay = document.createElement('div');
              spinnerOverlay.classList.add('spinner-overlay');
              spinnerOverlay.innerHTML = '<div class="spinner"></div>';
              aiSpecsFrame.appendChild(spinnerOverlay);

              // Call API to generate steps
              fetch('/generateTutorSteps', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: step2Text })
              })
                .then(response => response.json())
                .then(data => {
                  const steps = data.steps;
                  const parsedSteps = parseSteps(steps);
                  generatedSteps = parsedSteps;

                  // Hide spinner overlay
                  aiSpecsFrame.removeChild(spinnerOverlay);

                  currentStep++;
                  saveState()
                  updateStep();

                })
                .catch(error => {
                  console.error('Error:', error);
                  aiSpecsFrame.removeChild(spinnerOverlay);
                });
            } else {
              currentStep++;
              saveState()
              updateStep();
            }
          } else {
            currentStep++;
            saveState()
            updateStep();
          }
        }

        function backStep() {
          if (currentStep === 3) {
            while (stepsContainer.firstChild) {
              stepsContainer.removeChild(stepsContainer.firstChild);
            }

          } else if (currentStep === 2) {
            step2Text = aiSpecsTextarea.value;
          }
          currentStep--;
          saveState()
          updateStep();
        }

        currentStep = 0;
        currentLayout = false
        stepCounter = 0;

        const aiSpecsFrame = document.getElementById("aiSpecs");
        aiSpecsFrame.style.display = 'block';
        aiSpecsFrame.classList.add("expanded");
        const draftModal = document.getElementById("draftModal"); // Select the 
        const aiSpecsTextarea = document.querySelector('#aiSpecs textarea');
        const nextButton = document.getElementById("next");
        const regenButton = document.getElementById("regenerate");
        const luckyButton = document.getElementById("feelLucky");
        const backButton = document.getElementById("back");
        const cancelButton = document.getElementById("cancel");
        const aiSpecsButtonContainer = document.querySelector('#aiSpecs .button-container');

        step1Text = '';
        step2Text = '';
        generatedSteps = [];
        previousGeneratedSteps = []; // Array to store previous sets of generated steps

        const stepsContainer = document.createElement('div');
        stepsContainer.id = 'stepsContainer';
        stepsContainer.classList.add("steps-container");
        aiSpecsFrame.insertBefore(stepsContainer, aiSpecsFrame.firstChild); // Add stepsContainer initially


        const savedState = loadState();

        function load_step(step) {

          if (step === 0) {
            var modal = document.getElementById("draftModal");
            modal.style.display = "block";
            document.getElementById("aiGuided").onclick = function () {
              currentStep = 1
              saveState()
              load_step(currentStep);
            }
            aiSpecsFrame.style.display = 'none';


          }
          else if (step === 1 || step === 2) {

            draftModal.style.display = "block";
            document.querySelector('.button-container').style.display = 'none'; // 
            aiSpecsFrame.style.display = 'block';
            aiSpecsFrame.classList.add("expanded");
            draftModal.classList.add("expanded");
            aiSpecsTextarea.style.display = 'block';
            stepsContainer.style.display = 'none';
            regenButton.classList.add("hidden");
            luckyButton.classList.add("hidden");
            aiSpecsFrame.classList.remove("extra-expanded");
            draftModal.classList.remove("extra-expanded");
            aiSpecsButtonContainer.classList.remove("extra-expanded")
            if (step === 1) {
              currentStep = 1
              aiSpecsTextarea.placeholder = "Enter the initial question here...";
              backButton.style.display = 'none'; // Hide "Back" on first step
              aiSpecsTextarea.value = step1Text;
            } else {
              currentStep = 2
              aiSpecsTextarea.placeholder = "Enter additional instructions or questions here...";
              backButton.style.display = 'block';
              aiSpecsTextarea.value = step2Text;

            }
            cancelButton.style.display = 'block';
            nextButton.style.display = 'block';
            nextButton.textContent = "Next"; // Reset "Next" button text
          }
          else if (step === 3) {
            currentStep = 3
            // Show the third step
            document.querySelector('.button-container').style.display = 'none'; // 

            draftModal.style.display = "block";

            aiSpecsFrame.classList.add("extra-expanded");
            draftModal.classList.add("extra-expanded");
            aiSpecsButtonContainer.classList.add("extra-expanded");
            regenButton.classList.remove("hidden");
            luckyButton.classList.remove("hidden");

            regenButton.onclick = regenerateSteps;
            aiSpecsTextarea.style.display = 'none';
            nextButton.textContent = "Generate Tutor Drafts"
            nextButton.onclick = generateLayoutDrafts;
            backButton.style.display = 'block';

            stepsContainer.style.display = 'flex';
            // Add Regenerate button
            // Add Regenerate but
            if (generatedSteps.length === 0) {
              // Only add the initial step if there are no generated steps

              addStepBox();
            } else {

              // Add the generated steps to the stepsContainer
              generatedSteps.forEach(step => {
                addStepBox(step);
              });
            }
          }

          else if (step === 4) {
            currentStep = 4
            // Directly show the grid view without opening the modal
            loadLayoutDraft()
            console.log(currentLayout)

            if(currentLayout || currentLayout===0){
              
              showFullLayout(currentLayout)
            }
            
          }


        }


        nextButton.onclick = function () {
          if (currentStep === 1) {
            step1Text = aiSpecsTextarea.value;
            currentStep++;
            saveState()
            updateStep();
          } else if (currentStep === 2) {
            step2Text = aiSpecsTextarea.value;
            if (generatedSteps.length === 0) {
              // Show spinner overlay in step 2
              const spinnerOverlay = document.createElement('div');
              spinnerOverlay.classList.add('spinner-overlay');
              spinnerOverlay.innerHTML = '<div class="spinner"></div>';
              aiSpecsFrame.appendChild(spinnerOverlay);

              // Call API to generate steps
              fetch('/generateTutorSteps', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: step2Text })
              })
                .then(response => response.json())
                .then(data => {
                  const steps = data.steps;
                  const parsedSteps = parseSteps(steps);
                  generatedSteps = parsedSteps;

                  // Hide spinner overlay
                  aiSpecsFrame.removeChild(spinnerOverlay);

                  currentStep++;
                  saveState()
                  updateStep();
                })
                .catch(error => {
                  console.error('Error:', error);
                  aiSpecsFrame.removeChild(spinnerOverlay);
                });
            } else {
              currentStep++;
              saveState()
              updateStep();
            }
          } else {
            currentStep++;
            saveState()
            updateStep();
          }
        };

        backButton.onclick = function () {
          if (currentStep === 3) {
            while (stepsContainer.firstChild) {
              stepsContainer.removeChild(stepsContainer.firstChild);
            }

          } else if (currentStep === 2) {
            step2Text = aiSpecsTextarea.value;
          }
          currentStep--;
          saveState()
          updateStep();
        };

        
        if (savedState && savedState.currentTutor) {
          currentTutor = savedState.currentTutor
          document.querySelector("#page-container").innerHTML = currentTutor
          const element = document.getElementById('playground');
          // Remove the width style property
          element.style.width = '70%';


          document.getElementById("drag_drop").classList.remove("display-none")
          document.getElementById("drag-drop-section").classList.remove("display-none")
          document.getElementById("control-bar").classList.remove("hidden")

        }
        else if (savedState && savedState.aiGuidedActive) {
          currentStep = savedState.currentStep;
          currentLayout = savedState.currentLayout;
          step1Text = savedState.step1Text;
          step2Text = savedState.step2Text;
          generatedSteps = savedState.generatedSteps;
          aiGuidedActive = savedState.aiGuidedActive;
          generatedDrafts = savedState.generatedDrafts;
          load_step(currentStep)
        }
        else {
          // Start a new AI-guided drafting session
          var modal = document.getElementById("draftModal");
          modal.style.display = "block";
          aiSpecsFrame.style.display = 'none';

          document.getElementById("aiGuided").onclick = function () {
            currentStep = 1
            saveState()
            load_step(currentStep);

          };

        }




        // Handle cancel button in AI specs
        document.getElementById("cancel").onclick = function () {
          aiSpecsFrame.classList.remove("expanded");
          draftModal.classList.remove("expanded");
          aiSpecsFrame.classList.remove("extra-expanded");
          draftModal.classList.remove("extra-expanded");
          document.querySelector('.button-container').style.display = 'flex'; // Show initial buttons
          document.getElementById("aiSpecs").style.display = 'none'; // Hide AI specs
          document.getElementById("aiGuided").onclick = function () {
            currentStep = 1
            saveState()
            load_step(currentStep);
          }
          currentStep = 0
          saveState()
        }



      }

      // Close modal function
      function closeModal() {
        draftModal = document.getElementById("draftModal");
        draftModal.style.display = "none";
      }
      // Handle manual button
      document.getElementById("manual").onclick = function () {
        console.log("Manual drafting selected");
        closeModal();
      }










      function addMessageToChat(sender, text) {
        var chatMessages = document.querySelector('.chat-messages');
        var messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + (sender === "user" ? 'user-message' : 'bot-message');
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);

        // Scroll to the latest message
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }

      const componentsList = document.getElementById("components-list");

      // Function to toggle component details
      componentsList.addEventListener("click", function (e) {
        if (
          e.target.classList.contains("component-header") ||
          e.target.classList.contains("arrow-toggle")
        ) {
          const header = e.target.classList.contains("component-header")
            ? e.target
            : e.target.closest(".component-header");
          const details = header.nextElementSibling;
          const isVisible = details.style.display === "block";
          details.style.display = isVisible ? "none" : "block";
          header.querySelector(".arrow-toggle").textContent = isVisible
            ? "▼"
            : "▲";
        }
      });





      // Double-click to rename component
      componentsList.addEventListener("dblclick", function (e) {
        if (e.target.classList.contains("component-name")) {
          e.target.contentEditable = true;
          e.target.focus();
        }
      });

      // Event listener for when the renaming is done (on blur)
      componentsList.addEventListener(
        "blur",
        function (e) {
          if (
            e.target.classList.contains("component-name") &&
            e.target.contentEditable === "true"
          ) {
            const oldName = e.target.dataset.oldName;
            const newName = e.target.textContent.trim();

            // Update the dictionary with the new name
            updateComponentNameInDictionary(oldName, newName);

            // Update the id of the details container
            let detailsContainer = e.target
              .closest(".component-item")
              .querySelector(".component-details-container");
            if (detailsContainer) {
              detailsContainer.id = `${newName}-details-container`;
            }

            // Find and rename gallery item ids
            let galleryItems = detailsContainer.querySelectorAll(
              `[id^='galleryItem_${oldName.trim()}']`
            );
            galleryItems.forEach((item) => {
              let parts = item.id.split("_");
              if (parts.length === 3) {
                parts[1] = newName; // Replace the old component name with the new one
                item.id = parts.join("_"); // Join the parts back together
              }
            });

            e.target.contentEditable = false;
            delete e.target.dataset.oldName; // Clean up
          }
        },
        true
      );
      let history = [document.querySelector("#page-container").innerHTML]; // This will store the states
      let currentStateIndex = 0; // This will track the current state

      function applyState(state) {
        // Apply your state (e.g., update the DOM with the state content)
        const pageContainer = document.querySelector("#page-container");
        pageContainer.innerHTML = state; // Assuming state is the innerHTML content of page-container
      }

      function makeChange() {
        if (!isPinLayout && !isLikeLayout) {
          const newState = document.querySelector("#page-container").innerHTML;

          // Keep only the last 20 states
          while (history.length > 20) {
            history.shift();
          }

          // Truncate any future states if we're in the middle of the history
          if (currentStateIndex < history.length - 1) {
            history = history.slice(0, currentStateIndex + 1);
          }

          // Add the new state to the history and apply it
          history.push(newState);
          currentStateIndex++;
          applyState(newState);
        }
      }

      function undo() {
        if (currentStateIndex > 0) {
          currentStateIndex--;
          applyState(history[currentStateIndex]);
        } else {
          console.log("No more states to undo");
        }
      }

      function redo() {
        if (currentStateIndex < history.length - 1) {
          currentStateIndex++;
          applyState(history[currentStateIndex]);
        } else {
          console.log("No more states to redo");
        }
      }

      function restart() {
        if (localStorage){
          localStorage.clear()}
      location.reload();


      }

      // Example usage:
      // Call makeChange() whenever there's a change to the #page-container you want to save.

      // Call undo() and redo() when you want to navigate through the saved states.

      let lastBackspaceTime = 0;
      const doubleBackspaceThreshold = 500; // Time in milliseconds for double press

      // Function to handle the actual deletion logic
      function handleDoubleBackspaceAction(event) {
        deleteComponentHandler(event);
      }


      function cleanSelected() {
        if (selectedElements.length > 0) {
          for (var i = 0; i < selectedElements.length; i++) {
            // //console.log("for loop!!!", allNames.length);
            selectedElements[i].classList.remove("clicked")
          }
          selectedElements.splice(0, selectedElements.length);


        }
      }

      document.addEventListener("keydown", function (event) {
        const key = event.key;
        const currentTime = Date.now();
        const target = event.target; // Directly work with the event target
        const targetTagName = target.tagName.toLowerCase();
        const isContentEditable = target.isContentEditable; // Check if the target is contentEditable

        // Check if the pressed key is backspace and the focus is not on input/textarea, and also not on a contentEditable element
        if (
          key === "Backspace" &&
          !["input", "textarea"].includes(targetTagName) &&
          !isContentEditable // Ensure it's not a contentEditable element
        ) {
          // Check if the current press is within the threshold of the last press
          if (currentTime - lastBackspaceTime <= doubleBackspaceThreshold) {
            // Prevent the default backspace action
            event.preventDefault();
            // Handle the double backspace action
            handleDoubleBackspaceAction();
          }
          // Update the lastBackspaceTime to the current time
          lastBackspaceTime = currentTime;
        }



        if (key === 'Escape') {
          toggleCopyMode(false)
          //enableHoverFeedback() 
          if (dummyElement && dummyElement.parentNode) {
            dummyElement.parentNode.removeChild(dummyElement);
          }

          cleanSelected()

        }

        if (event.key === 'c' && (event.metaKey || event.ctrlKey)) {
          if (selectedElements.length == 1) {

            copyItem = selectedElements[0]
            toggleCopyMode(true)
          }

          // Optional: Provide visual feedback that copy mode is activated
        }


      }


      );



      // Function to update the component name in the dictionary
      function updateComponentNameInDictionary(oldName, newName) {
        // If the old name exists in the dictionary, update it
        if (componentCounts.hasOwnProperty(oldName)) {
          // If the new name is already in the dictionary, increment its count by the old count
          if (componentCounts.hasOwnProperty(newName)) {
            componentCounts[newName] += componentCounts[oldName];
          } else {
            // If the new name is not in the dictionary, add it and set its count to the old count
            componentCounts[newName] = componentCounts[oldName];
          }
          // Delete the old name from the dictionary
          delete componentCounts[oldName];
        }

        // Log the name change for debugging
        console.log("Component names updated in dictionary: ", componentCounts);
      }

      // Prevent drag on contenteditable elements
      componentsList.addEventListener("dragstart", function (e) {
        if (e.target.contentEditable === "true") {
          e.preventDefault();
        }
      });
      // Add component functionality
      document
        .getElementById("add-component-btn")
        .addEventListener("click", function () {
          const componentsList = document.getElementById("components-list");

          // Assuming 'componentCount' is a global dictionary tracking component counts
          const componentNames = document.querySelectorAll(".component-name");
          let maxNum = 0;

          componentNames.forEach((elem) => {
            const match = elem.textContent.match(/Component (\d+)/i);
            if (match && match[1]) {
              const num = parseInt(match[1], 10);
              if (num > maxNum) {
                maxNum = num;
              }
            }
          });

          const nextNum = maxNum + 1;
          const newComponentName = `Component ${nextNum}`;
          componentCounts[newComponentName] = 0; // Add new component with count 0 to the dictionary

          const newComponent = document.createElement("div");
          newComponent.className = "component-item border rounded-2 my-3";
          newComponent.draggable = false;
          newComponent.innerHTML = `
                    <div class="component-header d-flex justify-content-between align-items-center">
                        <span class="component-name" contenteditable="false" style="font-weight: bold; font-size: 20px;">${newComponentName}</span>
                        <span class="arrow-toggle">&#9660;</span>
                    </div>
                    <div class="component-details flex-column border rounded-2">
                        <div class="component-details-container bg-light p-2 border rounded-2" id="${newComponentName}-details-container">
                        <div class="spinner-overlay" style="display: none">
                        <div class="spinner"></div>
                     </div>
                            <ul class="component-details-content" data-type="page-items"> </ul>
                            <div class="container mx-auto flex flex-col py-1 justify-center items-center"></div>
                        </div>
                        <div class="input-group mt-3 p-2">
                            <input type="text" class="form-control" placeholder="Describe the component..."
                                aria-label="Component input"/>
                            <div class="input-group-append">
                                <button class="btn generate_component_btn btn-details rounded-button me-2" type="button">Generate</button>
                                <button class="btn btn-clear rounded-button me-2" type="button">Clear</button>
                                <button class="btn btn-delete rounded-button" type="button">Delete</button>
                            </div>
                        </div>
                    </div>
                `;

          componentsList.appendChild(newComponent);
          // Find the newly added .component-details-content within newComponent
          const newDetailsContent = newComponent.querySelector(
            ".component-details-content"
          );
          newComponent
            .querySelectorAll(".component-details-container")
            .forEach((container) => {
              container.addEventListener("click", onClickHandler, false);
            });

          // Instantiate a Dragoned_Component for it and add to the list
          instantiateAndAddToDragonedList(newDetailsContent);
        });

      function changeIDHandlerLog(event) {
        LOG.push(
          create_log_item(
            "Tutor Building",
            "Tutor",
            TUTOR_ID,
            "Change Element ID",
            concat(string(EditItem.id), "->", string(event.target.value))
          )
        );
      }

      function changeComponentValueLog(event) {
        LOG.push(
          create_log_item(
            "Tutor Building",
            "Tutor",
            TUTOR_ID,
            "Change Element Value",
            EditItem.id
          )
        );
      }

      function changeInputValueLog(event) {
        LOG.push(
          create_log_item(
            "Tutor Building",
            "Tutor",
            TUTOR_ID,
            "Change Input Value",
            EditItem.id
          )
        );
      }



      // Call the function to adjust the height
      function toggleSection(buttonId, sectionId) {
        var section = document.getElementById(sectionId);
        var button = document.getElementById(buttonId);

        // Check if the section is currently visible
        if (section.style.display === "none") {
          // If it's not visible, show it and update button style
          section.style.display = "block";
          button.classList.add("btn-dark");
          button.classList.remove("btn-light");
        } else {
          // If it's visible, hide it and update button style
          section.style.display = "none";
          button.classList.add("btn-light");
          button.classList.remove("btn-dark");
        }
      }

      function dragStartHandler(event) {
        if (EditItem) {
          EditItem.classList.remove("clicked");
        }

        event.dataTransfer.effectsAllowed = "copy";
        // event.dataTransfer.setData('text', ev.target.getAttribute('id'));
        dragItem = event.target;
        event.dataTransfer.setData("text/html", dragItem.id);
        // //console.log("DragstartId : ", dragItem.id);
        data = dragItem.id;
        sourceContainer = dragItem.parentNode;
        //console.log("drag started!!!");
        LOG.push(
          create_log_item(
            "Tutor Building",
            "Tutor",
            TUTOR_ID,
            "Drag Start",
            dragItem.id
          )
        );
        // alert(dragItem.classList);
        dragItem.classList.add("active");
      }

      function deleteComponentHandler(event) {
        if (selectedElements.length > 0) {
          for (var i = 0; i < selectedElements.length; i++) {
            // //console.log("for loop!!!", allNames.length);
            let index = allNames.indexOf(selectedElements[i].id);
            allNames.splice(index, 1);
            selectedElements[i].remove()

          }
          selectedElements.splice(0, selectedElements.length);
          component = document.getElementById(EditItem.id)
          EditItem.remove();
          LOG.push(
            create_log_item(
              "Tutor Building",
              "Tutor",
              TUTOR_ID,
              "Delete",
              component
            )
          );

        }
      }



      let pinnedElements = [];
      let likedElements = [];

      function isChildOfLayoutContent(element) {
        if (element.id === 'layout-content') {
          return false;  // layout-content is not considered a child of itself
        }

        let currentElement = element.parentElement;  // Start with the parent
        while (currentElement) {
          if (currentElement.id === 'layout-content') {
            return true;  // Found layout-content as a parent
          }
          currentElement = currentElement.parentElement;
        }
        return false;  // Reached the top without finding layout-content
      }

      function onClickHandler(event) {
        if (copyMode) {
          clickCopy(event);
          toggleCopyMode(false);
          return;
        }

        LOG.push(
          create_log_item(
            "Tutor Building",
            "Tutor",
            TUTOR_ID,
            "Element Clicked",
            event.target.id
          )
        );

        if (
          event.target.id == "page-container" ||
          event.target.classList.contains("component-details-content") ||
          event.target.id == "page"
        ) {
          return;
        }

        EditItem = event.target;

        if (
          event.target.classList.contains("form-control") ||
          event.target.classList.contains("page-item") ||
          event.target.classList.contains("page-item-ul") ||
          event.target.classList.contains("page-item-rl-row")
        ) {
          EditItem = EditItem.parentNode;
        }

        createID = EditItem.id;

        if (!allNames.includes(createID)) {
          allNames.push(createID);
        }

        if (isPinLayout || isLikeLayout) {
          if (isChildOfLayoutContent(EditItem)) {
            if (isPinLayout) {
              handlePinSelection(EditItem);
            } else {
              handleLikeSelection(EditItem);
            }
          } else {
            console.log("Selected element is not a child of layout-content. Pin/Like action ignored.");
          }
        } else {
          handleNormalSelection(EditItem, event.shiftKey);
        }
      }

      function isChildOfLayoutContent(element) {
        if (element.id === 'layout-content') {
          return false;  // layout-content is not considered a child of itself
        }

        let currentElement = element.parentElement;  // Start with the parent
        while (currentElement) {
          if (currentElement.id === 'layout-content') {
            return true;  // Found layout-content as a parent
          }
          currentElement = currentElement.parentElement;
        }
        return false;  // Reached the top without finding layout-content
      }

      function onClickHandler(event) {
        if (copyMode) {
          clickCopy(event);
          toggleCopyMode(false);
          return;
        }

        LOG.push(
          create_log_item(
            "Tutor Building",
            "Tutor",
            TUTOR_ID,
            "Element Clicked",
            event.target.id
          )
        );

        if (
          event.target.id == "page-container" ||
          event.target.classList.contains("component-details-content") ||
          event.target.id == "page"
        ) {
          return;
        }

        EditItem = event.target;

        if (
          event.target.classList.contains("form-control") ||
          event.target.classList.contains("page-item") ||
          event.target.classList.contains("page-item-ul") ||
          event.target.classList.contains("page-item-rl-row")
        ) {
          EditItem = EditItem.parentNode;
        }

        createID = EditItem.id;

        if (!allNames.includes(createID)) {
          allNames.push(createID);
        }

        if (isPinLayout || isLikeLayout) {
          if (isChildOfLayoutContent(EditItem)) {
            if (isPinLayout) {
              handlePinSelection(EditItem);
            } else {
              handleLikeSelection(EditItem);
            }
          } else {
            console.log("Selected element is not a child of layout-content. Pin/Like action ignored.");
          }
        } else {
          handleNormalSelection(EditItem, event.shiftKey);
        }
      }

      function checkParents(element, action) {
        let currentElement = element.parentElement;
        while (currentElement && currentElement.id !== 'layout-content') {
          if (currentElement.hasAttribute('pointed')) {
            const pointedType = currentElement.getAttribute('pointed');


            if (pointedType === 'fix' && action === 'like') {
              alert(`A parent of this element is already pinned. It's not possible to ${action} a child of a pinned element.`);
              return true;
            }
            if (pointedType === 'fix' && action === 'pin') {
              const index = pinnedElements.indexOf(currentElement);
              pinnedElements.splice(index, 1);
              currentElement.classList.remove("pinClicked");
              currentElement.removeAttribute("pointed");
              return false;
            }

            if (action === 'like' && pointedType === 'pref') {

              const index = likedElements.indexOf(currentElement);
              console.log(index)
              likedElements.splice(index, 1);
              currentElement.classList.remove("likeClicked");
              currentElement.removeAttribute("pointed");
              return false;
            }
          }
          currentElement = currentElement.parentElement;
        }
        return false;
      }

      function handlePinSelection(element) {
        if (checkParents(element, 'pin')) {
          return;
        }

        const index = pinnedElements.indexOf(element);
        if (index > -1) {
          // Element is already pinned, remove it
          pinnedElements.splice(index, 1);
          element.classList.remove("pinClicked");
          element.removeAttribute("pointed");
        } else {
          // Add element to pinned list
          pinnedElements.push(element);
          element.classList.add("pinClicked");
          element.setAttribute("pointed", "fix");

          // Remove preference if the element was previously preferred
          const likedIndex = likedElements.indexOf(element);
          if (likedIndex > -1) {
            likedElements.splice(likedIndex, 1);
            element.classList.remove("likeClicked");
          }

          // Remove pins and preferences from all child elements
          const childrenWithPointed = element.querySelectorAll('[pointed]');
          childrenWithPointed.forEach(child => {
            if (child.getAttribute('pointed') === 'fix') {
              const childIndex = pinnedElements.indexOf(child);
              if (childIndex > -1) {
                pinnedElements.splice(childIndex, 1);
              }
              child.classList.remove("pinClicked");
            } else {
              const childIndex = likedElements.indexOf(child);
              if (childIndex > -1) {
                likedElements.splice(childIndex, 1);
              }
              child.classList.remove("likeClicked");
            }
            child.removeAttribute("pointed");
          });
        }
        // Update cursor
      }

      function handleLikeSelection(element) {
        if (checkParents(element, 'like')) {
          return;
        }

        const index = likedElements.indexOf(element);
        if (index > -1) {
          // Element is already liked, remove it
          likedElements.splice(index, 1);
          element.classList.remove("likeClicked");
          element.removeAttribute("pointed");
        } else {
          // Add element to liked list
          likedElements.push(element);
          element.classList.add("likeClicked");
          element.setAttribute("pointed", "pref");

          // Remove preference from all child elements
          const childrenLiked = element.querySelectorAll('[pointed="pref"]');
          childrenLiked.forEach(child => {
            const childIndex = likedElements.indexOf(child);
            if (childIndex > -1) {
              likedElements.splice(childIndex, 1);
            }
            child.classList.remove("likeClicked");
            child.removeAttribute("pointed");
          });
        }
        // Update cursor
      }
      function handleNormalSelection(element, isShiftKey) {
        if (!isShiftKey) {
          // Clear previous selection only if shift key is not pressed
          selectedElements.forEach(el => el.classList.remove("clicked"));
          selectedElements = [];
        }

        const index = selectedElements.indexOf(element);
        if (index > -1) {
          // Element is already selected, remove it
          selectedElements.splice(index, 1);
          element.classList.remove("clicked");
        } else {
          // Add element to selection
          selectedElements.push(element);
          element.classList.add("clicked");
        }
      }
      function changeIDHandler(event) {
        // //console.log("value : ", event.target.value);

        if (event.keyCode === 13) {
          for (var i = 0; i < allNames.length; i++) {
            // //console.log("for loop!!!", allNames.length);
            if (allNames[i] === event.target.value) {
              i++;
              alert("This id duplicated!,So you should be use other Id.");
              break;
            } else if (
              i === allNames.length - 1 &&
              allNames[allNames.length - 1] !== event.target.value
            ) {
              // LOG.push(create_log_item("Tutor Building", "Tutor"", TUTOR_ID, "Change Element ID", concat(string(EditItem.id), "->", string(event.target.value))));
              EditItem.id = event.target.value;
            }
          }

          //console.log("============",allNames);
        }
      }

      function changeComponentValue(event) {
        if (
          EditItem.firstChild !== null &&
          EditItem.firstChild.nodeName === "P"
        ) {
          EditItem.firstChild.innerHTML = event.target.value;
        } else if (EditItem.id.includes("inputItem")) {
          document.getElementById(EditItem.id).value = event.target.value;
          document
            .getElementById(EditItem.id)
            .setAttribute("value", event.target.value);
          //console.log(EditItem);
        }
        // LOG.push(create_log_item("Tutor Building", "Tutor"", TUTOR_ID, "Change Element Value", EditItem.id));
      }

      function changeInputValue(event) {
        // LOG.push(create_log_item("Tutor Building", "Tutor"", TUTOR_ID, "Change Input Value", EditItem.id));
        document.getElementById(EditItem.id).value = event.target.value;
        document
          .getElementById(EditItem.id)
          .setAttribute("value", event.target.value);
      }

      function updateNodeIds(node) {
        if (node.nodeName === "DIV") {
          // If it's a DIV, assign a new ID
          node.id = "newItem_" + item_count;
          item_count++;
        }

        // Recurse for each child node
        node.childNodes.forEach((child) => {
          updateNodeIds(child); // Use the same prefix for child nodes
        });
      }


      function clickCopy(event) {
        // Custom logic for when an item is dropped in the component gallery
        if (copyTarget) {
          if (dummyElement && dummyElement.parentNode) {
            dummyElement.parentNode.removeChild(dummyElement);

          }
          copyItem.classList.remove("clicked")
          //console.log("droptarget:", dropTarget);
          var nodeCopy = document.getElementById(copyItem.id).cloneNode(true);
          updateNodeIds(nodeCopy)


          const listItems = Array.from(copyTarget.children);
          let insertBeforeElement = null;

          if (copyTarget.classList.contains("page-item-rl-row")) {
            // Find the child element to insert the dummy element before
            for (const item of listItems) {
              const rect = item.getBoundingClientRect();
              const halfwayPoint = rect.y + rect.height / 2;

              // Check if the mouse pointer is above the halfway point of the child element
              if (event.clientY < halfwayPoint) {
                insertBeforeElement = item;
                break;
              }
            }
          }
          else if (copyTarget.classList.contains("page-item-ul")) {
            for (const item of listItems) {
              const rect = item.getBoundingClientRect();
              const halfwayPoint = rect.x + rect.width / 2; // Change to calculate the horizontal halfway point

              // Check if the mouse pointer is to the left of the halfway point of the child element
              if (event.clientX < halfwayPoint) {
                insertBeforeElement = item;
                break; // Found the target item, stop looping
              }
            }
          }



          // Insert the nodeCopy at the determined position
          if (insertBeforeElement) {
            copyTarget.insertBefore(
              nodeCopy,
              insertBeforeElement
            );
          }
          else {
            copyTarget.appendChild(nodeCopy); // Fallback to append at the end
          }

          makeChange();

        }

        LOG.push(
          create_log_item(
            "Tutor Building",
            "Tutor",
            TUTOR_ID,
            copyItem.id
          )
        );
        copyItem.classList.remove("active");
        copyTarget = null;
        copyItem = null;
        cleanSelected()

      }


      function dragEndHandler(event) {
        // Custom logic for when an item is dropped in the component gallery
        if (
          dropTarget &&
          (dropTarget.classList.contains("component-details-content") ||
            dropTarget.closest(".component-details-container"))
        ) {
          // Handle the drop inside the component gallery
          removeDummyElement();
          //console.log("droptarget:", dropTarget);
          // For logging
          var action_type = "Drag End Other";
          if (sourceContainer.id === "draggable") {
            var componentItem = dropTarget.closest(".component-item");
            // Get the component name from the 'component-name' span
            var componentName =
              componentItem.querySelector(".component-name").textContent;
            // Increment the count for this component
            incrementComponentCount(componentName);

            // Add the dragged element to the gallery
            // Assuming 'component-gallery-content' is the container where you want to add the elements
            var nodeCopy = document.getElementById(data).cloneNode(true);
            if (nodeCopy.firstElementChild.nodeName === "INPUT") {
              // For logging
              action_type = "Drag End Input";
              nodeCopy.firstElementChild.id = "inputItem_" + item_count;
            }
            nodeCopy.id =
              "galleryItem_" +
              componentName +
              "_" +
              componentCounts[componentName];

            dropTarget.appendChild(nodeCopy);
            //adjustColumnHeight();

            makeChange();
            //console.log(nodeCopy.firstElementChild.nodeName);
          }
        } else if (dropTarget) {
          removeDummyElement();
          //console.log("droptarget:", dropTarget);
          // For logging
          var action_type = "Drag End Other";
          if (data.startsWith("galleryItem_")) {
            //console.log(nodeCopy.firstElementChild.nodeName);
            var nodeCopy = document.getElementById(data).cloneNode(true);
            // Assume 'galleryItem_' prefix indicates special handling, such as keeping certain attributes
            updateNodeIds(nodeCopy); // Recursively update IDs for the node and its children

            dropTarget.appendChild(nodeCopy);
          } else if (
            document
              .querySelector("#page-container")
              .contains(document.getElementById(data))
          ) {


            const listItems = Array.from(dropTarget.children);
            let insertBeforeElement = null;

            if (dropTarget.classList.contains("page-item-rl-row")) {
              // Find the child element to insert the dummy element before
              for (const item of listItems) {
                const rect = item.getBoundingClientRect();
                const halfwayPoint = rect.y + rect.height / 2;

                // Check if the mouse pointer is above the halfway point of the child element
                if (event.clientY < halfwayPoint) {
                  insertBeforeElement = item;
                  break;
                }
              }
            }
            else if (dropTarget.classList.contains("page-item-ul")) {
              for (const item of listItems) {
                const rect = item.getBoundingClientRect();
                const halfwayPoint = rect.x + rect.width / 2; // Change to calculate the horizontal halfway point

                // Check if the mouse pointer is to the left of the halfway point of the child element
                if (event.clientX < halfwayPoint) {
                  insertBeforeElement = item;
                  break; // Found the target item, stop looping
                }
              }
            }



            // Insert the nodeCopy at the determined position
            if (insertBeforeElement) {
              dropTarget.insertBefore(
                document.getElementById(data),
                insertBeforeElement
              );
            } else {
              dropTarget.appendChild(document.getElementById(data)); // Fallback to append at the end
            }

            makeChange();
          } else if (sourceContainer.id === "draggable") {
            var nodeCopy = document.getElementById(data).cloneNode(true);
            nodeCopy.id = "newItem_" + item_count;

            if (nodeCopy.firstElementChild.nodeName === "INPUT") {
              action_type = "Drag End Input";
              nodeCopy.firstElementChild.id = "inputItem_" + item_count;
            }
            item_count++;

            const listItems = Array.from(dropTarget.children);
            let insertBeforeElement = null;

            if (dropTarget.classList.contains("page-item-rl-row")) {
              // Find the child element to insert the dummy element before
              for (const item of listItems) {
                const rect = item.getBoundingClientRect();
                const halfwayPoint = rect.y + rect.height / 2;

                // Check if the mouse pointer is above the halfway point of the child element
                if (event.clientY < halfwayPoint) {
                  insertBeforeElement = item;
                  break;
                }
              }
            }
            else if (dropTarget.classList.contains("page-item-ul")) {
              for (const item of listItems) {
                const rect = item.getBoundingClientRect();
                const halfwayPoint = rect.x + rect.width / 2; // Change to calculate the horizontal halfway point

                // Check if the mouse pointer is to the left of the halfway point of the child element
                if (event.clientX < halfwayPoint) {
                  insertBeforeElement = item;
                  break; // Found the target item, stop looping
                }
              }
            }



            // Insert the nodeCopy at the determined position
            if (insertBeforeElement) {
              dropTarget.insertBefore(
                nodeCopy,
                insertBeforeElement
              );
            }
            else {
              dropTarget.appendChild(nodeCopy); // Fallback to append at the end
            }

            makeChange();
          } else {
            //console.log("Drop Target : ", dropTarget);
          }
          LOG.push(
            create_log_item(
              "Tutor Building",
              "Tutor",
              TUTOR_ID,
              action_type,
              dragItem.id
            )
          );
          dragItem.classList.remove("active");
          dropTarget = null;
          dragItem = null;
        } else {
          dragItem.classList.remove("active");
        }
      }
      function dropHandler(event) {
        //console.log("Droppped ....");
      }

      function removeDummyElement() {
        if (dropTarget && dropTarget.contains(dummyElement)) {
          dropTarget.removeChild(dummyElement);
        }
      }

      const draggable = new Dragoned(document.querySelector("#draggable"), {
        sort: false,
        clone: true,
        group: "blocks-group",
      });

      const editable = new Dragoned_Component(
        document.querySelector("#page-container"),
        {
          sort: false,
          clone: true,
          group: "blocks-group",
        }
      );
      // Example function to toggle copy mode and bind/unbind copyOverHandler
      function toggleCopyMode(activate) {
        copyMode = activate;
        const label = document.getElementById('copyModeLabel');

        const pageContainer = document.getElementById('page_parent');

        if (copyMode) {
          pageContainer.classList.add('copy-mode-border');
          pageContainer.classList.remove('border');
          label.style.display = 'block';

          // Assuming `editable` is your instance of Dragoned_Component
          editable.container.addEventListener('mouseover', editable.copyOverHandler);
          editable.container.removeEventListener('dragover', editable.dragOverHandler);

        } else {
          pageContainer.classList.remove('copy-mode-border');
          label.style.display = 'none';

          editable.container.addEventListener('dragover', editable.dragOverHandler);

          editable.container.removeEventListener('mouseover', editable.copyOverHandler);
        }
      }
      let dragonedComponentsList = []; // Initialize an empty array to hold the instances

      document
        .querySelectorAll(".component-details-content")
        .forEach((element) => {
          let instance = new Dragoned_Component(element, {
            sort: false,
            clone: true,
            group: "blocks-group",
          });
          dragonedComponentsList.push(instance); // Add the instance to the list
        });

      function instantiateAndAddToDragonedList(element) {
        let instance = new Dragoned_Component(element, {
          sort: false,
          clone: true,
          group: "blocks-group",
        });
        dragonedComponentsList.push(instance);
      }



    })();
  });
});
/**
 * Creates a log item object representing an action taken by an actor on a component.
 * This function is useful for tracking user actions or system events for auditing or debugging purposes.
 *
 * @param {string} component - The component on which the action is performed (e.g., a specific module or system part).
 * @param {string} actor - The entity performing the action (e.g., a user, system process).
 * @param {string|number} actor_id - A unique identifier for the actor.
 * @param {string} action_type - The type of action performed (e.g., "update", "delete").
 * @param {string|number} action_value - The value or outcome of the action (e.g., the new value after an update).
 * @returns {Object} An object representing the log item, including a timestamp, the component, actor, actor ID, action type, and action value.
 */
function create_log_item(
  component,
  actor,
  actor_id,
  action_type,
  action_value
) {
  return {
    time_stamp: new Date().toLocaleString(),
    component: component,
    actor: actor,
    actor_id: actor_id,
    action_type: action_type,
    action_value: action_value,
  };
}

function get_request_body(
  tutor_id,
  tutor_name = null,
  content = null,
  log_items = null
) {
  return {
    tutor_id: tutor_id,
    tutor_name: tutor_name,
    content: content,
    log_items: LOG,
  };
}
