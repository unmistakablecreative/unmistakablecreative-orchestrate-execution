#target photoshop

try {
    // Capture input parameters
    var args = arguments;
    var guestNameFileFormat;

    // Use the guest name provided as input, or throw an error if missing
    if (args.length < 1) {
        throw new Error("Guest name not provided. Ensure the script is called with the guest name as an argument.");
    } else {
        guestNameFileFormat = args[0];
    }

    // Define file paths based on guest name
    var coverAssetsFolder = "/Users/srinirao/Dropbox/2. Areas of Responsibility/Unmistkable Creative/1.Podcast/Covers/Assets/";
    var finishedCoversFolder = "/Users/srinirao/Dropbox/2. Areas of Responsibility/Unmistkable Creative/1.Podcast/Covers/Finished Covers/";
    var templateFilePath = new File(coverAssetsFolder + "UCCoverTemplate.psd");
    var backgroundFilePath = new File(coverAssetsFolder + guestNameFileFormat + "-bg.jpg");
    var artFilePath = new File(coverAssetsFolder + guestNameFileFormat + "-art.jpg");
    var outputFilePath = new File(finishedCoversFolder + guestNameFileFormat + "-cover.jpg");

    // Function to open a document, throwing an error if the file is missing
    function openDocument(filePath) {
        if (!filePath.exists) {
            throw new Error("File not found: " + filePath.fsName);
        }
        return app.open(filePath);
    }

    // Open the required documents
    $.writeln("Opening template...");
    var templateDoc = openDocument(templateFilePath);

    $.writeln("Opening background...");
    var backgroundDoc = openDocument(backgroundFilePath);

    $.writeln("Opening art...");
    var artDoc = openDocument(artFilePath);

    // Set the template as the active document
    app.activeDocument = templateDoc;

    // Run the recorded Photoshop action
    var actionSetName = "PodcastArt";  // Ensure the action set name matches exactly
    var actionName = "Action 2";      // Ensure the action name matches exactly
    $.writeln("Running action: " + actionSetName + " > " + actionName);
    app.doAction(actionName, actionSetName);

    // Export the final cover
    $.writeln("Exporting final cover...");
    var jpegOptions = new JPEGSaveOptions();
    jpegOptions.quality = 12; // Maximum quality
    templateDoc.saveAs(outputFilePath, jpegOptions, true);

    // Close all documents without saving changes
    $.writeln("Closing documents...");
    templateDoc.close(SaveOptions.DONOTSAVECHANGES);
    backgroundDoc.close(SaveOptions.DONOTSAVECHANGES);
    artDoc.close(SaveOptions.DONOTSAVECHANGES);

    // Success message
    $.writeln("Cover successfully exported to: " + outputFilePath.fsName);
} catch (e) {
    // Log any errors to the console
    $.writeln("Error: " + e.message);
    throw e;
}
