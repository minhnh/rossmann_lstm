/*
 * city.h
 *
 *  Created on: Nov 20, 2015
 *      Author: elhe
 */

#ifndef _ASSIGNMENT09_CITY_H_
#define _ASSIGNMENT09_CITY_H_

#include <string>

using namespace std;

class City {
    private:
        string name;
        float x;
        float y;
        float deadline;

    public:
        City(float x, float y, float deadline);
        City(const City & city);
        ~City();
        const string& getName() const;
        void setName(const string& name);
        double getX() const;
        void setX(float coord);
        double getY() const;
        void setY(float coord);
};

#endif /* _ASSIGNMENT09_CITY_H_ */
