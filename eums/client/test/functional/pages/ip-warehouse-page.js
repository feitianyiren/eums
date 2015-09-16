var EC = protractor.ExpectedConditions;
var IpWarehousePage = function () {};

IpWarehousePage.prototype = Object.create({}, {
    url: { get: function () { return '#/ip-items'; }},
    visit: { value: function () {
        browser.get(this.url);
    }},

    searchBar: { get: function () {
        return element(by.id('filter'));
    }},

    searchForItem: { value: function (searchTerm) {
        var EC = protractor.ExpectedConditions;
        var loadingCog = element(by.css('.glyphicon-cog'));
        var searchReady = EC.and(EC.visibilityOf(this.searchBar), EC.stalenessOf(loadingCog));

        browser.wait(searchReady, 5000, "Timeout exceeded while waiting for search to be ready");
        this.searchBar.clear().sendKeys(searchTerm);
        browser.sleep(2000);
        browser.wait(searchReady, 5000, "Timeout exceeded while retrieving search results");
    }},

    warehouseItemCount: { get: function () {
        return element.all(by.repeater('($index, item) in items')).count();
    }},

    itemDescriptions: { get: function () { return element.all(by.repeater('($index, item) in items').column('item.itemDescription')).getText(); }},
    itemBalances: { get: function () { return element.all(by.repeater('($index, item) in items').column('item.availableBalance')).getText(); }},

    reportOnFirstItem: { value: function () {
        element.all(by.css('.viewDelivery')).get(0).click();
    }},
    viewFirstItem: { value: function () {
        element.all(by.css('.reportDelivery')).get(0).click();
    }},

    itemName: { get: function () { return element(by.id('itemNameLabel')).getText(); }},
    itemAvailableQty: { get: function () { return element(by.id('itemQtyLabel')).getText(); }},

    specifyShipmentDate: { value: function (date) {
        element(by.css('#input-delivery-date input')).clear().sendKeys(date);
    }},
    specifyConsignee: { value: function (input) {
        fillSelect2Chosen('input-consignee', input);
    }},
    specifyContact: { value: function (input) {
        fillSelect2Chosen('input-contact', input);
    }},
    specifyLocation: { value: function (input) {
        fillSelect2Chosen('input-location', input);
    }},
    markAsEndUser: { value: function () {
        element(by.id('end-user-check')).click();
    }},

    specifyQuantity: { value: function (input) {
        element(by.id('quantity-shipped')).clear().sendKeys(input);
    }},

    saveDelivery: { value: function () { element(by.id('save-delivery-report')).click(); }},


    deliveryCount: { get: function () {
        return element.all(by.repeater('($index, node) in deliveryNodes')).count();
    }},

    deliveryQuantities: { get: function () { return element.all(by.repeater('').column('node.quantityIn')).getText(); }},
    deliveryDates: { get: function () { return element.all(by.repeater('').column('node.deliveryDate')).getText(); }},
    deliveryConsignees: { get: function () { return element.all(by.repeater('').column('node.consigneeName')).getText(); }},
    deliveryContacts: { get: function () { return element.all(by.repeater('').column('node.contactPerson.firstName')).getText(); }},
    deliveryLocations: { get: function () { return element.all(by.repeater('').column('node.location')).getText(); }}

});

module.exports = new IpWarehousePage;

function fillSelect2Chosen (id, input) {
    element(by.id(id)).click();
    element(by.css('.select2-input.select2-focused')).clear().sendKeys(input);
    element(by.css('.select2-results li')).click();
}
