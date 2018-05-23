const path = require("path");
const ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
    entry: [
        "./shipanaro/assets/shipanaro/js/index.js",
        "./shipanaro/assets/shipanaro/css/index.scss"
    ],
    output: {
        path: path.resolve(__dirname, "shipanaro/static/shipanaro"),
        filename: "js/main.js"
    },
    module: {
        rules: [
            {
                test: /\.scss$/,
                use: ExtractTextPlugin.extract({
                    fallback: 'style-loader',
                    use: ['css-loader', 'sass-loader']
                })
            }
        ]
    },
    plugins: [
        new ExtractTextPlugin({
            filename: "css/main.css"
        })
    ]
}