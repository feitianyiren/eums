var homePage = function () {
};

homePage.prototype = Object.create({}, {
    url: {
        get: function () {
            return '/';
        }
    },

    visit: {
        value: function () {
            browser.get(this.url);

            var EC = protractor.ExpectedConditions;
            var loadingModal = element(by.id('loading'));
            var fadingModal = element(by.css('.modal-backdrop.fade'));
            var mapHasLoaded = EC.and(EC.invisibilityOf(loadingModal), EC.stalenessOf(fadingModal));
            browser.wait(mapHasLoaded, 5000, "Timeout exceeded while loading map");
        }
    },

    pageTitle: {
        get: function () {
            return element(by.css('.white.navbar-brand')).getText();
        }
    },
    ipElement: {
        get: function () {
            return element(by.model('filter.programme'));
        }
    },
    map: {
        get: function () {
            return element(by.id('map'));
        }
    },
    mapLocation: {
        get: function () {
            return element(by.binding('totalStats.location')).getText();
        }
    },
    numberSent: {
        get: function () {
            return element(by.binding('data.totalStats.totalNumberOfDeliveries')).getText();
        }
    },
    numberDelivered: {
        get: function () {
            return element(by.binding('data.totalStats.numberOfSuccessfulProductDeliveries')).getText();
        }
    },
    numberNotDelivered: {
        get: function () {
            return element(by.binding('data.totalStats.numberOfUnsuccessfulProductDeliveries')).getText();
        }
    },
    numberNonResponse: {
        get: function () {
            return element(by.binding('data.totalStats.numberOfNonResponseToProductReceived')).getText();
        }
    },
    valueSent: {
        get: function () {
            return element(by.binding(' data.totalStats.totalValueOfDeliveries | compactCurrency ')).getText();
        }
    },
    valueDelivered: {
        get: function () {
            return element(by.binding(' data.totalStats.totalValueOfSuccessfulDeliveries | compactNumber ')).getText();
        }
    },
    valueNotDelivered: {
        get: function () {
            return element(by.binding(' data.totalStats.totalValueOfUnsuccessfulProductDeliveries | compactNumber ')).getText();
        }
    },
    valueNonResponse: {
        get: function () {
            return element(by.binding(' data.totalStats.totalValueOfNonResponseToProductReceived | compactNumber ')).getText();
        }
    },
    numberOfResponses: {
        get: function () {
            return element.all(by.repeater('response in responses'));
        }
    },
    responsesPageLink: {
        get: function () {
            return element(by.id('response-page-btn'));
        }
    },
    windmill: {
        get: function () {
            return element(by.id('loading'));
        }
    },

    clickMapLayer: {
        value: function (district) {
            browser.sleep(2000);
            browser.executeScript(function (district) {
                window.map.clickLayer(district);
            }, district);
            browser.sleep(2000);
        }
    },

    selectIpView: {
        value: function () {
            element(by.id('ip-view')).click();
            browser.sleep(2000);
        }
    },

    highLightMapLayer: {
        value: function (district) {
            browser.executeScript(function (district) {
                window.map.highlightLayer(district);
            }, district);
        }
    },

    getHighlightedLayer: {
        value: function () {
            return browser.executeScript(function (district) {
                return window.map.getHighlightedLayer(district);
            }, district).then(function (highlightedLayer) {
                return highlightedLayer;
            });
        }
    },

    getHighlightedLayerName: {
        value: function () {
            return browser.executeScript(function () {
                return window.map.getLayerName();
            }).then(function (highlightedLayerName) {
                return highlightedLayerName;
            });
        }
    },

    getHighlightedStyle: {
        value: function (district) {
            return browser.executeScript(function (district) {
                return window.map.getStyle(district);
            }, district).then(function (style) {
                return style;
            });
        }
    },

    enterImplementingPartnerToFilterBy: {
        value: function () {
            this.ipElement.sendKeys(selectedIp);
        }
    },

    getMapZoomLevel: {
        value: function () {
            browser.sleep(5000);
            return browser.executeScript(function () {
                return window.map.getZoom();
            }).then(function (zoomLevel) {
                return zoomLevel;
            });
        }
    },

    goToResponseDetailsPage: {
        value: function () {
            this.responsesPageLink.click();
        }
    },

    searchForProgramme: {
        value: function (searchTerm) {
            element(by.id('s2id_select-program')).click();
            element(by.css('.select2-input.select2-focused')).clear().sendKeys(searchTerm);
        }
    },

    programmeSearchResults: {
        get: function () {
            return element(by.css('.select2-results li')).getText();
        }
    },


    latestDeliveriesCount: {
        get: function () {
            return element.all(by.repeater('response in data.latestDeliveries')).count();
        }
    },

    latestDeliveryResponses: {
        get: function () {
            return element.all(by.repeater('response in data.latestDeliveries'));
        }
    },

    toast: {
        get: function () {
            return element(by.repeater('message in messages'));
        }
    },

    toastMessage: {
        get: function () {
            return element(by.repeater('message in messages')).getText();
        }
    },
});

module.exports = new homePage();