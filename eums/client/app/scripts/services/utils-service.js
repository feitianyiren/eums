angular.module('SysUtils', [])
    .factory('SysUtilsService', function () {
        return {
            formatDate: function (date) {
                try {
                    var result = "";
                    if (date.trim()) {
                        date = date.trim().replace(/\//g, "-");
                        result = moment(date).format('DD-MMM-YYYY')
                    }
                    if (result == "Invalid date") {
                        result = moment(date, "DD-MM-YYYY").format('DD-MMM-YYYY')
                    }
                    return result;
                } catch (err) {
                    return "";
                }
            }
        }
    });
