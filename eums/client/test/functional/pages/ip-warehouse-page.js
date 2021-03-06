var EC = protractor.ExpectedConditions;
var IpWarehousePage = function () {
};

IpWarehousePage.prototype = Object.create({}, {

    url: {
        get: function () {
            return '/#/ip-items';
        }
    },

    visit: {
        value: function () {
            browser.get(this.url);
        }
    },

    pageHeaderText: {
        get: function () {
            return element(by.id('page-header-text')).getText();
        }
    },

    searchBar: {
        get: function () {
            return element(by.id('filter'));
        }
    },

    searchForItem: {
        value: function (searchTerm) {
            var loadingCog = element(by.css('.glyphicon-cog'));
            var searchReady = EC.and(EC.visibilityOf(this.searchBar), EC.stalenessOf(loadingCog));

            browser.wait(searchReady, 5000, "Timeout exceeded while waiting for search to be ready");
            this.searchBar.clear().sendKeys(searchTerm);
            browser.sleep(2000);
            browser.wait(searchReady, 5000, "Timeout exceeded while retrieving search results");
        }
    },

    warehouseItemCount: {
        get: function () {
            return element.all(by.repeater('($index, item) in items')).count();
        }
    },

    itemDescriptions: {
        get: function () {
            return element.all(by.repeater('($index, item) in items').column('item.itemDescription')).getText();
        }
    },
    itemBalances: {
        get: function () {
            return element.all(by.repeater('($index, item) in items').column('item.availableBalance')).getText();
        }
    },

    firstItem: {
        get: function () {
            return {
                description: element(by.repeater('($index, item) in items').row(0).column('item.itemDescription')).getText(),
                balance: element(by.repeater('($index, item) in items').row(0).column('item.availableBalance')).getText()
            };
        }
    },

    viewFirstItem: {
        value: function () {
            element.all(by.css('.viewDelivery')).get(0).click();
            waitForPageToLoad();
        }
    },
    reportOnFirstItem: {
        value: function () {
            element.all(by.css('.reportDelivery')).get(0).click();
            waitForPageToLoad();
        }
    },
    createNewDeliveryToSelf: {
        value: function () {
            element.all(by.css('.assign-items-to-self')).get(0).click();
            waitForPageToLoad();
        }
    },

    itemName: {
        get: function () {
            return element(by.id('itemNameLabel')).getText();
        }
    },
    itemAvailableQty: {
        get: function () {
            return element(by.id('qty-available-label')).getText();
        }
    },

    notificationWarning: {
        get: function () {
            return element(by.css('.notification-warning'))
        }
    },

    specifyShipmentDate: {
        value: function (date) {
            element(by.css('#input-delivery-date input')).clear().sendKeys(date);
        }
    },
    specifyConsignee: {
        value: function (input) {
            fillSelect2Chosen('input-consignee', input);
        }
    },
    specifyContact: {
        value: function (input) {
            fillSelect2Chosen('input-contact', input);
        }
    },
    specifyLocation: {
        value: function (input) {
            fillSelect2Chosen('input-location', input);
        }
    },
    markAsNotEndUser: {
        value: function () {
            element(by.id('end-user-check')).click();
        }
    },
    isEndUserChecked: {
        get: function () {
            return element(by.id('end-user-check')).getAttribute('value');
        }
    },

    specifyQuantity: {
        value: function (input) {
            element(by.id('quantity-shipped')).clear().sendKeys(input);
        }
    },

    saveDelivery: {
        value: function () {
            element(by.id('save-delivery-report')).click();
            browser.sleep(2000);
        }
    },

    discardDelivery: {
        value: function () {
            element(by.id('discard-delivery-report')).click();
            waitForPageToLoad();
        }
    },

    deliveryCount: {
        get: function () {
            return element.all(by.repeater('($index, node) in deliveryNodes')).count();
        }
    },

    deliveryQuantities: {
        get: function () {
            return element.all(by.repeater('($index, node) in deliveryNodes').column('node.quantityIn')).getText();
        }
    },
    deliveryDates: {
        get: function () {
            return element.all(by.repeater('($index, node) in deliveryNodes').column('node.deliveryDate')).getText();
        }
    },
    deliveryConsignees: {
        get: function () {
            return element.all(by.repeater('($index, node) in deliveryNodes').column('node.consigneeName')).getText();
        }
    },
    deliveryContacts: {
        get: function () {
            return element.all(by.repeater('($index, node) in deliveryNodes').column('node.contactPerson.firstName')).getText();
        }
    },
    deliveryLocations: {
        get: function () {
            return element.all(by.repeater('($index, node) in deliveryNodes').column('node.location')).getText();
        }
    },

    createNewDelivery: {
        value: function () {
            element(by.id('create-new-delivery')).click();
            waitForPageToLoad();
        }
    },

    viewSubconsignees: {
        value: function () {
            element.all(by.css('.subconsignee-column')).get(0).click();
            waitForPageToLoad();
        }
    },

    addSubconsignee: {
        value: function () {
            element(by.id('new-subconsignee-btn')).click();
        }
    },

    specifySubQuantity: {
        value: function (input) {
            element(by.css('#quantity-shipped input')).clear().sendKeys(input);
        }
    },

    subDeliveryCount: {
        get: function () {
            return element.all(by.repeater('delivery in deliveries')).count();
        }
    },

    fullUrl: {
        value: function (partialUrl) {
            return browser.baseUrl + partialUrl;
        }
    },

    viewFirstSubconsignee: {
        value: function () {
            element.all(by.css('.viewSubConsignee')).get(0).click();
            waitForPageToLoad();
        }
    },

    subDeliveryQuantities: {
        get: function () {
            return element.all(by.repeater('delivery in deliveries').column('delivery.quantityIn')).getText();
        }
    },
    subDeliveryDates: {
        get: function () {
            return element.all(by.repeater('delivery in deliveries').column('delivery.deliveryDate')).getText();
        }
    },
    subDeliveryConsignees: {
        get: function () {
            return element.all(by.repeater('delivery in deliveries').column('delivery.consigneeName')).getText();
        }
    },
    subDeliveryContacts: {
        get: function () {
            return element.all(by.repeater('delivery in deliveries').column('delivery.contactPerson.firstName')).getText();
        }
    },
    subDeliveryLocations: {
        get: function () {
            return element.all(by.repeater('delivery in deliveries').column('delivery.location')).getText();
        }
    },

    breadCrumbs: {
        get: function () {
            return element.all(by.css('.breadcrumb li'));
        }
    }
});

module.exports = new IpWarehousePage;

function fillSelect2Chosen(id, input) {
    element(by.id(id)).click();
    element(by.css('.select2-input.select2-focused')).clear().sendKeys(input);
    element(by.id('select2-drop')).element(by.css('.select2-results li')).click();
}

function waitForPageToLoad() {
    var loadingModal = element(by.id('loading'));
    var fadingModal = element(by.css('.modal-backdrop.fade'));
    var pageHasLoaded = EC.and(EC.invisibilityOf(loadingModal), EC.stalenessOf(fadingModal));
    browser.wait(pageHasLoaded, 5000, "Timeout exceeded while loading page");
}
